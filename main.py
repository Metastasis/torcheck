import socket
from dpkt.ip import IP
from dpkt.tcp import TCP
from dpkt.ssl import TLS, SSL2
from netfilterqueue import NetfilterQueue
from random import randrange
from network_status import get_directory_addresses

LIBNETFILTER_QUEUE_NUM = 1

ip_list = {}

# IP protocol field constants
PROTO_TCP = 6
PROTO_TLS = 56
KNOWN_PROTO = [PROTO_TCP, PROTO_TLS]


# TODO: download list of dirs and do not block them
# TODO #2: check current algo
# TODO #3: if #2 does not work, try pass all from internal network, but block responses

def is_tor_port(port):
    return port == 443 or (port >= 9000 and port <= 9100)


def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


def modify_pkt_rnd(net_packet):
    # net.data is layer 4 packet
    # so net.data.data is layer 5 or just a payload of layer 4
    net = IP(net_packet.get_payload())
    tran_len = len(net.data)

    payload_len = net.len - tran_len
    if not payload_len:
        return net.pack()

    new_data = bytearray(net.data.pack())
    for idx in range(10):
        rnd_byte = randrange(0, payload_len)
        # God, please, i hope there's no off-by-one error
        new_data[(tran_len - payload_len) + rnd_byte] = rnd_byte
        # new_data[rnd_byte] = bytes([rnd_byte])

    net.data = new_data

    return net.pack()


def ingress_loop(packet):
    global ip_list
    global directories_ip
    global KNOWN_PROTO

    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    if network.p not in KNOWN_PROTO:
        print('[?] unknown protocol: {}'.format(network.p))
        packet.accept()
        return

    readable_ip = inet_to_str(network.src)
    transport = network.data

    # if type(transport) == TCP:
    #     print("[!] tcp")

    if not is_tor_port(transport.sport):
        print('[?] not relevant port: {}'.format(transport.sport))
        packet.accept()
        return

    if readable_ip in directories_ip:
        print('[*] found request for an authority, accepting...')
        packet.accept()
        return

    if readable_ip not in ip_list:
        print('[!] Blacklisting: {}'.format(readable_ip))
        ip_list[readable_ip] = 0

    ip_list[readable_ip] += 1
    if ip_list[readable_ip] % 3:
        modified_pkt = modify_pkt_rnd(packet)
        packet.set_payload(modified_pkt)

    packet.accept()
    return


def egress_loop(packet):
    global ip_list
    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    # if type(transport) == TCP:
    #     print("[!] tcp")

    if transport.dport == 443 or transport.dport >= 9000 and transport.dport <= 9100:
        print("[*] found relevant port: {}".format(transport.dport))

    if network.dst not in ip_list and len(ip_list) < 10:
        print('Blacklisting: {}, length: {}'.format(network.dst, len(ip_list)))
        ip_list.append(network.dst)

    if network.dst in ip_list:
        packet.drop()
        return

    packet.accept()

    print("[--------------------------]")


nfqueue = NetfilterQueue()
nfqueue.bind(LIBNETFILTER_QUEUE_NUM, ingress_loop)

# FIXME: cause we running filtering and tor client on the same machine
directories_ip = get_directory_addresses(use_hardcode=True)

try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("Terminated")

print(ip_list)
nfqueue.unbind()
