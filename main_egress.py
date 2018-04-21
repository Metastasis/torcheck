from dpkt.dpkt import UnpackError
from dpkt.http import Request, Response
from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from utils import inet_to_str  # , save_connections
from blacklist import Blacklist
from track.tracker_client import track_flow

LIBNETFILTER_QUEUE_NUM = 1

connections = {}


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
    #     print('[drop] {}:{} -> {}:{}'.format(flow[0], flow[1], flow[2], flow[3]))
    #     packet.drop()
    #     return

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    if transport.dport not in [80]:
        return packet.accept()

    # try:
    #     track_flow(('192.168.199.2', 10101), flow)
    # except:
    #     pass

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

    print('========= egress flows =========')
    for f, s in connections.items():
        flow_addresses = '{}:{},{}:{}'.format(f[0], f[1], f[2], f[3])
        print(flow_addresses)

    # save_connections(connections)

    nfqueue.unbind()
