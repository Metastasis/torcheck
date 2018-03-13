from dpkt.ip import IP
from dpkt.tcp import TCP
from dpkt.ssl import TLS, SSL2
from netfilterqueue import NetfilterQueue
from directory_ips import DA_IP_LIST

LIBNETFILTER_QUEUE_NUM = 1

counter = 0


def egress_loop(packet):
    global counter
    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    counter += 1

    transport = network.data

    if network.dst in DA_IP_LIST:
        print("[!] FOUND DA [!]")

    if type(transport) == TCP:
        print("[!] tcp")

    # if transport.dport == 443 or transport.dport >= 9000 and transport.dport <= 9100:
    #     print("[*] found relevant port: {}".format(transport.dport))

    if counter <= 10:
        packet.drop()
        return

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
