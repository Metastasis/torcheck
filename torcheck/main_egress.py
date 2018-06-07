from dpkt.dpkt import UnpackError
from dpkt.http import Request
from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from torcheck.utils import inet_to_str  # , save_connections
from torcheck.blacklist import Blacklist
from torcheck.track.client_log import ClientLog
from datetime import datetime
from torcheck.arguments import get_args_for_egress
from torcheck.configuration.base_config import BaseConfig
from torcheck.settings import PEERS_PATH

LIBNETFILTER_QUEUE_NUM = 1

connections = {}

KNOWN_PEERS = []


def egress_loop(packet, client_logger, blcklst, flows, callback):
    now = datetime.now()
    raw_packet = packet.get_payload()
    network = IP(raw_packet)

    transport = network.data

    src_ip = inet_to_str(network.src)
    dst_ip = inet_to_str(network.dst)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    if flow in flows:
        flows[flow] = flows[flow] + transport.data
    else:
        flows[flow] = transport.data

    flow_addresses = '{}:{},{}:{}'.format(src_ip, transport.sport, dst_ip, transport.dport)
    print(flow_addresses)

    tracked_client_arrived = client_logger.arrived_near(now)
    if tracked_client_arrived and dst_ip in KNOWN_PEERS:
        print('no RF, setting...')
        now = datetime.now()
        client_logger.log(now)
        network.rf = 1
        network.sum = 0
        packet.set_payload(bytes(network))
        packet.accept()
        return

    if not tracked_client_arrived or transport.dport not in [80, 443]:
        packet.accept()
        return

    if transport.dport == 443 and dst_ip in blcklst:
        del flows[flow]
        print('[drop] ssl blacklisted: IP: {}'.format(
            dst_ip
        ))
        if callback:
            callback(packet, network, True)
            return
        else:
            return packet.drop()

    try:
        stream = flows[flow]
        http = Request(stream)

        bad_host = http.headers['host']
        print(flow)

        if tracked_client_arrived and bad_host in blcklst:
            print('[drop] blacklisted host: {}, IP: {}'.format(
                bad_host,
                dst_ip
            ))
            del flows[flow]
            if callback:
                callback(packet, network, True)
                return
            else:
                return packet.drop()
        stream = stream[len(http):]
        if len(stream) == 0:
            del flows[flow]
        else:
            flows[flow] = stream
    except UnpackError:
        pass

    if callback:
        callback(packet, network, False)
    else:
        packet.accept()
    return


def egress_loop_wrapper(client_logger, blcklst, flows, callback):
    def _loop(packet):
        egress_loop(packet, client_logger, blcklst, flows, callback)

    return _loop


def main(known_peers=[], block_list=[], callback=None):
    """Main function

        Args:
            known_peers: list of IP addresses of known tor peers
            block_list: list of sites in format "<url>;<ip>"
            callback: it will be called with before decision making with next arguments:
            - NetfilterQueue packet object
            - Parsed dpkt ip object
            - Flag; True if packet should be blocked, otherwise False
    """
    global KNOWN_PEERS
    KNOWN_PEERS = []
    client_log = ClientLog()
    blacklist = Blacklist()

    if callback:
        KNOWN_PEERS = known_peers
        if not len(KNOWN_PEERS):
            raise ValueError("Known peers list is empty. You have to specify IP addresses of known peers")
        blacklist.update_list(block_list)
        if not len(blacklist):
            raise ValueError("Blacklist is empty. You have to specify blacklisted IP addresses")
    else:
        parser = get_args_for_egress()
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

    loop = egress_loop_wrapper(client_log, blacklist, connections, callback)
    nfqueue = NetfilterQueue()
    nfqueue.bind(LIBNETFILTER_QUEUE_NUM, loop)

    try:
        print("[*] waiting for data")
        nfqueue.run()
    except KeyboardInterrupt:
        print("Terminated")

    nfqueue.unbind()


if __name__ == "__main__":
    main()
