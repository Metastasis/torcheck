from dpkt.ip import IP
from dpkt.tcp import TCP
from dpkt.ssl import TLS, SSL2
from netfilterqueue import NetfilterQueue
from directory_ips import DA_IP_LIST
from random import randrange

LIBNETFILTER_QUEUE_NUM = 1

ip_list = []


def modify_pkt_rnd(net_packet):
    packet = net_packet.data

    for idx in range(10):
        rnd_byte = randrange(0, len(packet.data))
        packet.data[rnd_byte] = bytes([randrange(0, 128)])

    return net_packet.pack()


def ingress_loop(packet):
    global ip_list
    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    if network.src in DA_IP_LIST:
        print("[!] FOUND DA [!]")

    # if type(transport) == TCP:
    #     print("[!] tcp")

    if transport.sport == 443 or transport.sport >= 9000 and transport.sport <= 9100:
        print("[*] found relevant port: {}".format(transport.dport))

    if network.src not in ip_list and len(ip_list) < 10:
        print('Blacklisting: {}, length: {}'.format(network.dst, len(ip_list)))
        ip_list.append(network.dst)

    if network.src in ip_list:
        packet = modify_pkt_rnd(network)
        packet.drop()
        return

    packet.accept()

    print("[--------------------------]")


def egress_loop(packet):
    global ip_list
    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    if network.dst in DA_IP_LIST:
        print("[!] FOUND DA [!]")

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

try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("Terminated")

print(ip_list)
nfqueue.unbind()
