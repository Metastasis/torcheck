from dpkt.ip import IP
from dpkt.tcp import TCP
from dpkt.ssl import TLS, SSL2
from netfilterqueue import NetfilterQueue

LIBNETFILTER_QUEUE_NUM = 1


def egress_loop(packet):
    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    if type(transport) == TCP:
        print("[!] tcp")
    else:
        packet.accept()
        return

    if transport.dport == 443 or transport.dport >= 9000 and transport.dport <= 9100:
        print("[*] found relevant port: {}".format(transport.dport))

    packet.accept()

    print("[--------------------------]")


nfqueue = NetfilterQueue()
nfqueue.bind(LIBNETFILTER_QUEUE_NUM, egress_loop)

try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("Terminated")

nfqueue.unbind()
