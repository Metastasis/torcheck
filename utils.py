import socket
from dpkt.ip import IP
from random import randrange
from dpkt.dpkt import NeedData, UnpackError
from dpkt.http import Request, Response


def modify_pkt_rnd(net_packet):
    # net.data is layer 4 packet
    # so net.data.data is layer 5 or just a payload of layer 4
    net = IP(net_packet.get_payload())
    tran_len = len(net.data)

    payload_len = net.len - tran_len
    if not payload_len:
        return net.pack()

    new_data = bytearray(net.data.pack())
    for idx in range(10):
        rnd_byte = randrange(0, payload_len)
        # God, please, i hope there's no off-by-one error
        new_data[(tran_len - payload_len) + rnd_byte] = rnd_byte
        # new_data[rnd_byte] = bytes([rnd_byte])

    net.data = new_data

    return net.pack()


def is_tor_port(port):
    return port == 443 or (port >= 9000 and port <= 9100) or (port >= 8000 and port <= 8100)


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


def parse_http_stream(raw_stream):
    rest_stream = raw_stream

    try:
        stream = rest_stream
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
            return
        else:
            rest_stream = stream
    except UnpackError:
        pass
