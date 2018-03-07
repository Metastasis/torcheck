from dpkt.ip import IP
from netfilterqueue import NetfilterQueue

LIBNETFILTER_QUEUE_NUM = 1


def main_loop(packet):
    pkt = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    print(pkt)
    packet.accept()


nfqueue = NetfilterQueue()
nfqueue.bind(LIBNETFILTER_QUEUE_NUM, main_loop)

try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("Terminated")

nfqueue.unbind()
