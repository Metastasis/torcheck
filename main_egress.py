from dpkt.dpkt import UnpackError, in_cksum
from dpkt.http import Request, Response
from dpkt.ip import IP, IP_LEN_MAX
from netfilterqueue import NetfilterQueue
from utils import inet_to_str  # , save_connections
from blacklist import Blacklist
from ip_options import IPOption

LIBNETFILTER_QUEUE_NUM = 1

connections = {}

MARKER = b'\x66\x66\x66\x66\x66\x66\x66\x66'
MARKER_LEN = len(MARKER)
BYTE = 1

KNOWN_PEERS = [
    '10.0.10.4',
    '10.0.10.6',
    '10.0.10.7'
]

option_pointer = b'\x05'  # pointer
option_extra = b'\x01'  # overflow 0, flag - timestamp and address
# option_address = b'\x00\x00\x00\x00'  # address
# option_timestamp = b'\x00\x00\x00\x00'  # timestamp
option_data = option_pointer + option_extra
timestamp = IPOption(
    type=0xC4,  # should copy, class debugging and measurement, type timestamp
    length=0x0c,
    data=option_data
)

option_eol = b'\x00'  # End of Options List


# padding = size of options - (0x0C + 0x01)


def append_options(ip, new_option):
    has_options = len(ip.opts) > 0
    if has_options:
        return ip

    DWORD = 4  # bytes
    EOL_LEN = 1  # DWORD
    opts_len = (new_option.length / DWORD) + EOL_LEN  # DWORDS
    header_len = ip.hl + opts_len
    if header_len > 15:
        return ip

    opts_len = opts_len * DWORD  # bytes

    ip.hl = header_len
    ip.len = ip.len + opts_len
    ip.opts = bytes(new_option) + option_eol

    padding_len = opts_len - len(ip.opts)

    ip.opts = ip.opts + (b'\x00' * padding_len)
    ip.sum = in_cksum(ip.pack_hdr() + bytes(ip.opts))

    return ip


def egress_loop(packet):
    global connections
    global blacklist

    is_marked = False
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

    if MARKER in raw_packet:
        print('found marker')
        network.len = network.len - 8
        network.data = transport.pack()[:-MARKER_LEN]
        hdr = network.pack_hdr() + bytes(network.opts)
        network.sum = in_cksum(hdr)
        packet.set_payload(network.pack())
    elif dst_ip in KNOWN_PEERS and network.len < IP_LEN_MAX:
        is_marked = True
        print('creating marker')
        network.data = transport.pack() + MARKER
        network.len = len(network)
        network.sum = 0  # dpkt magic to recalc checksum
        packet.set_payload(bytes(network))

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
