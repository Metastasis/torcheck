from dpkt.dpkt import in_cksum
from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from utils import inet_to_str  # , save_connections
from blacklist import Blacklist
from datetime import datetime
from track.tracker_client import track_flow

LIBNETFILTER_QUEUE_NUM = 2

connections = {}

MARKER = b'\x66\x66\x66\x66\x66\x66\x66\x66'
MARKER_LEN = len(MARKER)
BYTE = 1

KNOWN_PEERS = [
    '10.0.10.4',
    '10.0.10.6',
    '10.0.10.7'
]


def ingress_loop(packet):
    global connections

    raw_packet = packet.get_payload()
    network = IP(packet.get_payload())
    transport = network.data
    is_marked = False
    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    # if network.p not in KNOWN_PROTO:
    #     print('[?] unknown protocol: {}'.format(network.p))
    #     packet.accept()
    #     return

    src_ip = inet_to_str(network.src)
    dst_ip = inet_to_str(network.dst)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    if MARKER in raw_packet:
        is_marked = True
        print('found marker')
        hdr = network.pack_hdr()
        network.len = network.len - BYTE
        print("before: {}".format(network.data))
        network.data = network.data[:-MARKER_LEN]
        print("after: {}".format(network.data))
        print()
        network.sum = in_cksum(hdr)
        packet.set_payload(network.pack())

    flow_addresses = '{}:{},{}:{}'.format(src_ip, transport.sport, dst_ip, transport.dport)
    print(flow_addresses)

    # try:
    #     stream = connections[flow]
    #     if stream[:4] == 'HTTP':
    #         http = Response(stream)
    #         # print(http.status)
    #     else:
    #         http = Request(stream)
    #         # print(http.method, http.uri)
    #
    #     print(http)
    #     print()
    #
    #     # If we reached this part an exception hasn't been thrown
    #     stream = stream[len(http):]
    #     if len(stream) == 0:
    #         del connections[flow]
    #     else:
    #         connections[flow] = stream
    # except UnpackError:
    #     pass

    packet.accept()
    # if is_marked:
    #     print('modified packet: {}'.format(packet.get_payload()))
    return


if __name__ == "__main__":
    blacklist = Blacklist()
    blacklist.load()

    nfqueue = NetfilterQueue()
    nfqueue.bind(LIBNETFILTER_QUEUE_NUM, ingress_loop)

    try:
        print("[*] waiting for data")
        nfqueue.run()
    except KeyboardInterrupt:
        print("Terminated")

    # print('========= ingress flows =========')
    # for f, s in connections.items():
    #     flow_addresses = '{}:{},{}:{}'.format(f[0], f[1], f[2], f[3])
    #     print(flow_addresses)

    # save_connections(connections)

    nfqueue.unbind()
