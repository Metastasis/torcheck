from dpkt.ip import IP
from dpkt.tcp import TCP
from dpkt.ssl import TLS, SSL2
from netfilterqueue import NetfilterQueue

LIBNETFILTER_QUEUE_NUM = 1


def main_loop(packet):
    packet.accept()
    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    if type(transport) == TCP:
        print("[!] tcp")

    if type(transport) == TLS:
        print("[!] tls")

    if type(transport) == SSL2:
        print("[!] sslv2")
    print("[--------------------------]")

nfqueue = NetfilterQueue()
nfqueue.bind(LIBNETFILTER_QUEUE_NUM, main_loop)

try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("Terminated")

nfqueue.unbind()
