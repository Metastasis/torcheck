from dpkt.dpkt import UnpackError
from dpkt.http import Request, Response
from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from utils import inet_to_str
from dump import save_connections
from blacklist import Blacklist
from urllib.parse import urlparse

LIBNETFILTER_QUEUE_NUM = 1

connections = {}


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
    global blacklist

    network = IP(packet.get_payload())

    # modify the packet all you want here
    # packet.set_payload(str(pkt)) #set the packet content to our modified version

    transport = network.data

    src_ip = inet_to_str(network.src)
    dst_ip = inet_to_str(network.dst)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    # if flow[3] in [443]:
    #     packet.drop()
    #     return

    if flow[3] not in [80]:
        packet.accept()
        return

    bad_ip = src_ip in blacklist or dst_ip in blacklist
    bad_host = None

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    try:
        stream = connections[flow]
        http = Request(stream)
        bad_host = urlparse(http.headers['host']).hostname

        print(flow)
        print(http.headers['host'], ' ', http.uri)
        print()

        # If we reached this part an exception hasn't been thrown
        stream = stream[len(http):]
        if len(stream) == 0:
            del connections[flow]
        else:
            connections[flow] = stream
    except UnpackError:
        pass

    if (bad_ip in blacklist) and (bad_host and bad_host in blacklist):
        print('found blacklisted host: {}, ip: {}'.format(bad_host, bad_ip))
        del connections[flow]
        return packet.drop()

    packet.accept()


blacklist = Blacklist()
blacklist.load()

nfqueue = NetfilterQueue()
nfqueue.bind(LIBNETFILTER_QUEUE_NUM, egress_loop)

try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("Terminated")

print('========= flows =========')
for f, s in connections.items():
    flow_addresses = '{}:{}_{}:{}'.format(f[0], f[1], f[2], f[3])
    print(flow_addresses)

# save_connections(connections)

nfqueue.unbind()
