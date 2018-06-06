from dpkt.dpkt import UnpackError
from dpkt.http import Request
from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from utils import inet_to_str  # , save_connections
from blacklist import Blacklist
from track.client_log import ClientLog
from datetime import datetime
from arguments import get_args_for_egress
from configuration.base_config import BaseConfig
from settings import PEERS_PATH

LIBNETFILTER_QUEUE_NUM = 1

connections = {}

KNOWN_PEERS = []


def egress_loop(packet):
    global connections
    global blacklist
    global client_log

    now = datetime.now()
    raw_packet = packet.get_payload()
    network = IP(raw_packet)

    transport = network.data

    src_ip = inet_to_str(network.src)
    dst_ip = inet_to_str(network.dst)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    flow_addresses = '{}:{},{}:{}'.format(src_ip, transport.sport, dst_ip, transport.dport)
    print(flow_addresses)

    tracked_client_arrived = client_log.arrived_near(now)
    if tracked_client_arrived and dst_ip in KNOWN_PEERS:
        print('no RF, setting...')
        network.rf = 1
        network.sum = 0
        packet.set_payload(bytes(network))
        packet.accept()
        return

    if not tracked_client_arrived or transport.dport not in [80]:
        packet.accept()
        return

    try:
        stream = connections[flow]
        http = Request(stream)

        bad_host = http.headers['host']
        print(flow)

        if tracked_client_arrived and bad_host in blacklist:
            print('[drop] blacklisted host: {}, IP: {}'.format(
                bad_host,
                dst_ip
            ))
            del connections[flow]
            return packet.drop()

        stream = stream[len(http):]
        if len(stream) == 0:
            del connections[flow]
        else:
            connections[flow] = stream
    except UnpackError:
        pass

    packet.accept()
    return


if __name__ == "__main__":
    KNOWN_PEERS = []
    parser = get_args_for_egress()
    client_log = ClientLog()
    blacklist = Blacklist()

    args = parser.parse_args()

    peers_cfg = BaseConfig()
    if args.peers is None:
        peers_cfg.load(PEERS_PATH)
    else:
        peers_cfg.load(args.peers)
        if len(peers_cfg.data):
            peers_cfg.save(PEERS_PATH)

    KNOWN_PEERS = peers_cfg.data
    if not len(KNOWN_PEERS):
        raise ValueError("Known peers list is empty. You have to specify IP addresses of known peers")

    if args.blacklist is None:
        blacklist.load()
    else:
        blacklist.load(args.blacklist)
        if len(blacklist):
            blacklist.save()

    if not len(blacklist):
        raise ValueError("Blacklist is empty. You have to specify blacklisted IP addresses")

    nfqueue = NetfilterQueue()
    nfqueue.bind(LIBNETFILTER_QUEUE_NUM, egress_loop)

    try:
        print("[*] waiting for data")
        nfqueue.run()
    except KeyboardInterrupt:
        print("Terminated")

    nfqueue.unbind()
