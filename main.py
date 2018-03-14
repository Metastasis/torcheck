import socket
from dpkt.ip import IP
from dpkt.tcp import TCP
from dpkt.ssl import TLS, SSL2
from netfilterqueue import NetfilterQueue
from random import randrange
from network_status import get_directory_addresses

LIBNETFILTER_QUEUE_NUM = 1

ip_list = []


# TODO: download list of dirs and do not block them
# TODO #2: check current algo
# TODO #3: if #2 does not work, try pass all from internal network, but block responses

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
    # so net.data.data is layer 5, i.e. payload of layer 4
    net = IP(net_packet.get_payload())

    for idx in range(10):
        if not len(net.data.data):
            return net.pack()
        payload_len = net.len - len(net.data)
        rnd_byte = randrange(0, payload_len)
        new_data = bytearray(net.data.data)
        new_data[rnd_byte] = randrange(0, 128)
        # new_data[rnd_byte] = bytes([randrange(0, 128)])
        net.data.data = new_data

    return net.pack()


def ingress_loop(packet):
    global ip_list
    global directories_ip
    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    readable_ip = inet_to_str(network.src)
    transport = network.data

    # if type(transport) == TCP:
    #     print("[!] tcp")

    if transport.sport == 443 or transport.sport >= 9000 and transport.sport <= 9100:
        print("[*] found relevant port: {}".format(transport.sport))

    if readable_ip in directories_ip:
        print('[*] found request for an authority, accepting...')
        packet.accept()
        return

    if readable_ip not in ip_list and len(ip_list) < 10:
        print('Blacklisting: {}, length: {}'.format(readable_ip, len(ip_list)))
        ip_list.append(readable_ip)

    if readable_ip in ip_list:
        modified_pkt = modify_pkt_rnd(packet)
        packet.set_payload(modified_pkt)
        packet.accept()
        return

    packet.accept()

    print("[--------------------------]")


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
