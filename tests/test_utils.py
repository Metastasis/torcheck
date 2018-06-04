from unittest import TestCase, main
from utils import inet_to_str, str_to_inet, is_valid_ipv4_address


class TestUtils(TestCase):
    def test_inet_to_str(self):
        result = '48.64.80.96'
        valid_ip = b'\x30\x40\x50\x60'
        self.assertEqual(result, inet_to_str(valid_ip))

    def test_str_to_inet(self):
        result = b'\x30\x40\x50\x60'
        valid_ip = '48.64.80.96'
        self.assertEqual(result, str_to_inet(valid_ip))

    def test_ipv4_validation(self):
        self.assertTrue(is_valid_ipv4_address('10.0.0.0'))
        self.assertFalse(is_valid_ipv4_address('10.0.0.0.'))
        self.assertFalse(is_valid_ipv4_address('10.0..0'))
        self.assertFalse(is_valid_ipv4_address('10.0.0.0.0'))


if __name__ == '__main__':
    main()
