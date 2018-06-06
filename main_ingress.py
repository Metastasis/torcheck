from dpkt.ip import IP
from netfilterqueue import NetfilterQueue
from utils import inet_to_str
from track.client_log import ClientLog
from datetime import datetime
from arguments import get_args_for_ingress

LIBNETFILTER_QUEUE_NUM = 2

connection_flows = {}


def ingress_loop(packet, client_logger, connections):
    now = datetime.now()
    network = IP(packet.get_payload())
    transport = network.data

    src_ip = inet_to_str(network.src)
    dst_ip = inet_to_str(network.dst)
    flow = (src_ip, transport.sport, dst_ip, transport.dport)

    if flow in connections:
        connections[flow] = connections[flow] + transport.data
    else:
        connections[flow] = transport.data

    flow_addresses = '{}:{},{}:{}'.format(src_ip, transport.sport, dst_ip, transport.dport)
    print(flow_addresses)

    if network.rf:
        print('got RF set, logging into file...')
        client_logger.log(now)

    return packet.accept()


def ingress_loop_wrapper(client_logger, connections):
    def _loop(packet):
        ingress_loop(packet, client_logger, connections)

    return _loop


if __name__ == "__main__":
    parser = get_args_for_ingress()
    client_log = ClientLog()

    args = parser.parse_args()
    client_log.clean()

    loop = ingress_loop_wrapper(client_log, connection_flows)
    nfqueue = NetfilterQueue()
    nfqueue.bind(LIBNETFILTER_QUEUE_NUM, loop)

    try:
        print("[*] waiting for data")
        nfqueue.run()
    except KeyboardInterrupt:
        print("Terminated")

    nfqueue.unbind()
