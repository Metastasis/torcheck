from dpkt.dpkt import in_cksum
from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from utils import inet_to_str
from blacklist import Blacklist
from ip_options import IPOption, append_options

LIBNETFILTER_QUEUE_NUM = 2

connections = {}

MARKER = b'\x66\x66\x66\x66'
MARKER_LEN = len(MARKER)
BYTE = 1

KNOWN_PEERS = [
    '10.0.10.4',
    '10.0.10.6',
    '10.0.10.7'
]

TRACKED_CLIENTS = [
    '10.0.10.5'
]

# option_address = b'\x00\x00\x00\x00'  # address
# option_timestamp = b'\x00\x00\x00\x00'  # timestamp
# padding = size of options - (0x0C + 0x01)


def ingress_loop(packet):
    global connections

    network = IP(packet.get_payload())
    transport = network.data

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

    flow_addresses = '{}:{},{}:{}'.format(src_ip, transport.sport, dst_ip, transport.dport)
    print(flow_addresses)

    can_modify = transport.seq > 0 and transport.ack > 0
    if can_modify:
        if network.rf:
            print('got RF set')
        elif src_ip in KNOWN_PEERS:
            print('found tracked user, setting RF...')
            network.rf = 1
            network.sum = 0
            packet.set_payload(bytes(network))

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

    return packet.accept()


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
