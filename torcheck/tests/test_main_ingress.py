from unittest import TestCase, main
from unittest.mock import MagicMock
from dpkt.ip import IP, IP_PROTO_TCP
from dpkt.tcp import TCP
from torcheck.utils import str_to_inet
from torcheck import main_ingress
from torcheck.track.client_log import ClientLog


class PacketMock:
    def accept(self):
        pass

    def drop(self):
        pass

    def get_payload(self):
        pass

    def set_payload(self):
        pass


class TestMainIngress(TestCase):
    def setUp(self):
        main_ingress.TRACKED_CLIENTS = ['130.10.20.24', '130.10.20.25']
        self.mock_packet = PacketMock()
        self.mock_packet.accept = MagicMock(return_value=True)
        self.mock_packet.drop = MagicMock(return_value=True)
        self.mock_logger = ClientLog()
        self.mock_logger.log = MagicMock(return_value='logged')

    def test_client_logged_when_ip_matched(self):
        src = str_to_inet(main_ingress.TRACKED_CLIENTS[0])
        random_ip = b'\x01\x02\x03\x04'
        first_ip_packet = IP(id=0, src=src, dst=random_ip, p=IP_PROTO_TCP)
        first_tcp_packet = TCP(sport=7000, dport=7000, data=b'\x05\x04\x03\x02\x01')
        first_ip_packet.data = first_tcp_packet

        connections = {}
        self.mock_packet.get_payload = MagicMock(return_value=bytes(first_ip_packet))
        loop = main_ingress.ingress_loop_wrapper(self.mock_logger, connections)
        loop(self.mock_packet)

        self.mock_logger.log.assert_called_once()
        self.mock_packet.accept.assert_called_once()

    def test_client_logged_when_rf_flag_is_set(self):
        src_ip = b'\x01\x02\x03\x04'
        dst_ip = b'\x05\x06\x07\x08'
        first_ip_packet = IP(id=0, src=src_ip, dst=dst_ip, rf=1, p=IP_PROTO_TCP)
        first_tcp_packet = TCP(sport=7000, dport=7000, data=b'\x05\x04\x03\x02\x01')
        first_ip_packet.data = first_tcp_packet

        connections = {}
        self.mock_packet.get_payload = MagicMock(return_value=bytes(first_ip_packet))
        loop = main_ingress.ingress_loop_wrapper(self.mock_logger, connections)
        loop(self.mock_packet)

        self.mock_logger.log.assert_called_once()
        self.mock_packet.accept.assert_called_once()


if __name__ == '__main__':
    main()
