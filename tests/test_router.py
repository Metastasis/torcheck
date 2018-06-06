from unittest import TestCase, main
from unittest.mock import MagicMock
from dpkt.ip import IP, IP_PROTO_TCP
from dpkt.tcp import TCP
from utils import str_to_inet
import main_router


class PacketMock:
    def accept(self):
        pass

    def drop(self):
        pass

    def get_payload(self):
        pass

    def set_payload(self):
        pass


class TestRouter(TestCase):
    def setUp(self):
        main_router.TRACKED_CLIENTS = ['130.10.20.24', '130.10.20.25']
        main_router.TOR_PEERS = ['99.10.20.30', '128.0.0.128']
        self.mock_packet = PacketMock()
        self.mock_packet.accept = MagicMock(return_value=True)
        self.mock_packet.drop = MagicMock(return_value=True)

    def test_client_should_not_be_tracked(self):
        src_ip = b'\x01\x02\x03\x04'
        dst_ip = b'\x05\x06\x07\x08'
        first_ip_packet = IP(id=0, src=src_ip, dst=dst_ip, p=IP_PROTO_TCP)
        first_ip_packet.data = TCP(sport=1024, dport=2048, data=b'\x05\x04\x03\x02\x01')

        self.mock_packet.get_payload = MagicMock(return_value=bytes(first_ip_packet))
        main_router.ingress_loop(self.mock_packet)

        self.mock_packet.accept.assert_called_once()

    def test_client_should_be_tracked_but_he_requests_not_tor(self):
        src_ip = str_to_inet(main_router.TRACKED_CLIENTS[0])
        dst_ip = b'\x01\x02\x03\x04'
        first_ip_packet = IP(id=0, src=src_ip, dst=dst_ip, p=IP_PROTO_TCP)
        first_ip_packet.data = TCP(sport=1024, dport=2048, data=b'\x05\x04\x03\x02\x01')

        self.mock_packet.get_payload = MagicMock(return_value=bytes(first_ip_packet))
        main_router.ingress_loop(self.mock_packet)

        self.mock_packet.accept.assert_called_once()

    def test_client_is_tracked_and_marked(self):
        src_ip = str_to_inet(main_router.TRACKED_CLIENTS[0])
        dst_ip = str_to_inet(main_router.TOR_PEERS[0])
        first_ip_packet = IP(id=0, src=src_ip, dst=dst_ip, p=IP_PROTO_TCP)
        first_ip_packet.data = TCP(sport=1024, dport=2048, data=b'\x05\x04\x03\x02\x01')

        self.mock_packet.get_payload = MagicMock(return_value=bytes(first_ip_packet))
        self.mock_packet.set_payload = MagicMock(return_value=None)

        main_router.ingress_loop(self.mock_packet)

        call = self.mock_packet.set_payload.call_args_list[0]
        args, kwargs = call
        ip_packet = IP(args[0])

        self.mock_packet.set_payload.assert_called_once()
        self.mock_packet.accept.assert_called_once()
        self.assertEqual(ip_packet.rf, 1, 'Reserved flag is not set')


if __name__ == '__main__':
    main()
