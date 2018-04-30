from dpkt.dpkt import UnpackError, in_cksum
from dpkt.http import Request, Response
from dpkt.ip import IP, IP_LEN_MAX
from netfilterqueue import NetfilterQueue
from utils import inet_to_str  # , save_connections
from blacklist import Blacklist
from datetime import datetime
from track.tracker_client import track_flow

LIBNETFILTER_QUEUE_NUM = 1

connections = {}

MARKER = b'\x00\x00\x00\x00\xde\xad\xbe\xaf'
MARKER_LEN = len(MARKER)
BYTE = 1

KNOWN_PEERS = [
    '10.0.10.4',
    '10.0.10.6',
    '10.0.10.7'
]


def egress_loop(packet):
    global connections
    global blacklist

    raw_packet = packet.get_payload()
    network = IP(raw_packet)

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    src_ip = inet_to_str(network.src)
    dst_ip = inet_to_str(network.dst)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    # if flow[3] in [443]:
    #     print('[drop] {}:{} -> {}:{}'.format(flow[0], flow[1], flow[2], flow[3]))
    #     packet.drop()
    #     return

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    flow_addresses = '{}:{},{}:{}'.format(src_ip, transport.sport, dst_ip, transport.dport)
    print(flow_addresses)

    if raw_packet[-MARKER_LEN:] == MARKER:
        print('found marker: {}'.format(packet[-MARKER_LEN:]))
        hdr = network.pack_hdr()
        network.len = network.len - BYTE
        network.data = transport.pack()
        network.sum = in_cksum(hdr)
        packet.set_payload(network.pack())
    elif dst_ip in KNOWN_PEERS and network.len < IP_LEN_MAX:
        print('creating marker')
        hdr = network.pack_hdr()
        print(packet.get_payload())
        network.len = network.len + BYTE
        network.data = transport.pack() + MARKER
        network.sum = in_cksum(hdr)
        packet.set_payload(network.pack())
        print(packet.get_payload())

    if transport.dport not in [80]:
        return packet.accept()

    # try:
    #     track_flow(('192.168.199.2', 10101), flow)
    # except:
    #     pass

    try:
        stream = connections[flow]
        http = Request(stream)
        if src_ip in blacklist:
            bad_ip = src_ip
        elif dst_ip in blacklist:
            bad_ip = dst_ip
        else:
            bad_ip = 'not listed'

        bad_host = http.headers['host']

        print(flow)
        print(bad_host, ' ', http.uri)
        print()

        if bad_host in blacklist:
            print('[drop] blacklisted host: {}, IP: {}, IP (blacklist): {}'.format(bad_host, dst_ip, bad_ip))
            del connections[flow]
            return packet.drop()

        # If we reached this part an exception hasn't been thrown
        stream = stream[len(http):]
        if len(stream) == 0:
            del connections[flow]
        else:
            connections[flow] = stream
    except UnpackError:
        pass

    packet.accept()


if __name__ == "__main__":
    blacklist = Blacklist()
    blacklist.load()

    nfqueue = NetfilterQueue()
    nfqueue.bind(LIBNETFILTER_QUEUE_NUM, egress_loop)

    try:
        print("[*] waiting for data")
        nfqueue.run()
    except KeyboardInterrupt:
        print("Terminated")

    # print('========= egress flows =========')
    # for f, s in connections.items():
    #     flow_addresses = '{}:{},{}:{}'.format(f[0], f[1], f[2], f[3])
    #     print(flow_addresses)

    # save_connections(connections)

    nfqueue.unbind()
