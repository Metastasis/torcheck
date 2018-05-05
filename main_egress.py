from dpkt.dpkt import UnpackError, in_cksum
from dpkt.http import Request, Response
from dpkt.ip import IP, IP_LEN_MAX
from netfilterqueue import NetfilterQueue
from utils import inet_to_str  # , save_connections
from blacklist import Blacklist
from ip_options import IPOption, append_options

LIBNETFILTER_QUEUE_NUM = 1

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


def egress_loop(packet):
    global connections
    global blacklist

    options_appended = False
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

    if len(network.opts):
        print('got options: {}'.format(network.opts))
    elif dst_ip in KNOWN_PEERS:
        print('no options, adding...')
        options_appended = True
        option_pointer = b'\x0D'  # pointer
        option_extra = b'\x00'  # overflow 0, flag - timestamp and address
        data = option_pointer + option_extra + b'\x33\x33\x33\x33' + MARKER
        option = IPOption(
            type=0x44,
            length=0x0c,
            data=data
        )
        new_ip = append_options(network, option)
        packet.set_payload(bytes(new_ip))

    if transport.dport not in [80]:
        packet.accept()
        # if is_marked: print(packet.get_payload())
        return

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
    # if is_marked: print(packet.get_payload())
    return


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
