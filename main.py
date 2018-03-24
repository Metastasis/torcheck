from dpkt.dpkt import NeedData, UnpackError
from dpkt.http import Request, Response
from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from utils import inet_to_str
from dump import save_connections

LIBNETFILTER_QUEUE_NUM = 1

ip_list = {}
connections = {}
# IP protocol field constants
PROTO_TCP = 6
PROTO_TLS = 56
KNOWN_PROTO = [PROTO_TCP, PROTO_TLS]


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
    dst_ip = inet_to_str(network.src)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    try:
        stream = connections[flow]
        if stream[:4] == 'HTTP':
            http = Response(stream)
            # print(http.status)
        else:
            http = Request(stream)
            # print(http.method, http.uri)

        print(http)
        print()

        # If we reached this part an exception hasn't been thrown
        stream = stream[len(http):]
        if len(stream) == 0:
            del connections[flow]
        else:
            connections[flow] = stream
    except UnpackError:
        pass

    packet.accept()
    return


def egress_loop(packet):
    global connections

    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    src_ip = inet_to_str(network.src)
    dst_ip = inet_to_str(network.dst)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    if flow[4] not in [80]:
        packet.accept()
        return

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    try:
        stream = connections[flow]
        http = Request(stream)
        print(flow)
        print(http.method, http.uri)
        print()

        # If we reached this part an exception hasn't been thrown
        stream = stream[len(http):]
        if len(stream) == 0:
            del connections[flow]
        else:
            connections[flow] = stream
    except UnpackError:
        pass

    packet.accept()
    return


nfqueue = NetfilterQueue()
nfqueue.bind(LIBNETFILTER_QUEUE_NUM, egress_loop)

try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("Terminated")

print(connections.keys())

# save_connections(connections)

nfqueue.unbind()
