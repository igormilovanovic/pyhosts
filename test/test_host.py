import unittest

from pyhosts import Host
from netaddr import IPAddress
from netaddr.core import AddrFormatError


class TestHost(unittest.TestCase):
    """Test suite for Host class covering valid/invalid inputs, string representations, and equality checks."""

    def test_host_creation_with_ipv4(self):
        """Test creating a Host with valid IPv4 address."""
        host = Host('192.168.1.1', 'example', None, None)
        self.assertEqual(IPAddress('192.168.1.1'), host.ipaddress)
        self.assertEqual('example', host.hostname)
        self.assertIsNone(host.aliases)
        self.assertIsNone(host.comments)

    def test_host_creation_with_ipv6(self):
        """Test creating a Host with valid IPv6 address."""
        host = Host('::1', 'localhost6', None, None)
        self.assertEqual(IPAddress('::1'), host.ipaddress)
        self.assertEqual('localhost6', host.hostname)
        self.assertIsNone(host.aliases)
        self.assertIsNone(host.comments)

    def test_host_creation_with_aliases_string(self):
        """Test creating a Host with aliases as a string."""
        host = Host('127.0.0.1', 'localhost', 'local myhost', None)
        self.assertEqual(IPAddress('127.0.0.1'), host.ipaddress)
        self.assertEqual('localhost', host.hostname)
        self.assertEqual(['local', 'myhost'], host.aliases)
        self.assertIsNone(host.comments)

    def test_host_creation_with_single_alias(self):
        """Test creating a Host with a single alias."""
        host = Host('10.0.0.1', 'server', 'srv', None)
        self.assertEqual(['srv'], host.aliases)

    def test_host_creation_with_comments(self):
        """Test creating a Host with comments."""
        host = Host('192.168.1.100', 'webserver', None, 'production server')
        self.assertEqual(IPAddress('192.168.1.100'), host.ipaddress)
        self.assertEqual('webserver', host.hostname)
        self.assertIsNone(host.aliases)
        self.assertEqual('production server', host.comments)

    def test_host_creation_with_all_fields(self):
        """Test creating a Host with all fields populated."""
        host = Host('172.16.0.1', 'gateway', 'gw router', 'main gateway')
        self.assertEqual(IPAddress('172.16.0.1'), host.ipaddress)
        self.assertEqual('gateway', host.hostname)
        self.assertEqual(['gw', 'router'], host.aliases)
        self.assertEqual('main gateway', host.comments)

    def test_host_creation_with_empty_aliases_string(self):
        """Test creating a Host with empty string for aliases."""
        host = Host('192.168.1.1', 'example', '', None)
        self.assertIsNone(host.aliases)

    def test_invalid_ipv4_address(self):
        """Test that invalid IPv4 address raises AddrFormatError."""
        with self.assertRaises(AddrFormatError):
            Host('999.999.999.999', 'invalid', None, None)

    def test_invalid_ipv6_address(self):
        """Test that invalid IPv6 address raises AddrFormatError."""
        with self.assertRaises(AddrFormatError):
            Host('gggg::1', 'invalid', None, None)

    def test_invalid_ip_format(self):
        """Test that completely invalid IP format raises AddrFormatError."""
        with self.assertRaises(AddrFormatError):
            Host('not-an-ip', 'invalid', None, None)

    def test_repr_minimal(self):
        """Test __repr__ method with minimal fields."""
        host = Host('127.0.0.1', 'localhost', None, None)
        expected = str({'ipaddress': IPAddress('127.0.0.1'),
                        'hostname': 'localhost',
                        'aliases': None,
                        'comments': None})
        self.assertEqual(expected, repr(host))

    def test_repr_with_aliases(self):
        """Test __repr__ method with aliases."""
        host = Host('192.168.1.1', 'server', 'srv web', None)
        expected = str({'ipaddress': IPAddress('192.168.1.1'),
                        'hostname': 'server',
                        'aliases': ['srv', 'web'],
                        'comments': None})
        self.assertEqual(expected, repr(host))

    def test_repr_with_all_fields(self):
        """Test __repr__ method with all fields."""
        host = Host('10.0.0.1', 'gateway', 'gw', 'main router')
        expected = str({'ipaddress': IPAddress('10.0.0.1'),
                        'hostname': 'gateway',
                        'aliases': ['gw'],
                        'comments': 'main router'})
        self.assertEqual(expected, repr(host))

    def test_str_minimal(self):
        """Test __str__ method with minimal fields."""
        host = Host('127.0.0.1', 'localhost', None, None)
        expected = '127.0.0.1\tlocalhost\n'
        self.assertEqual(expected, str(host))

    def test_str_with_aliases(self):
        """Test __str__ method with aliases."""
        host = Host('192.168.1.1', 'server', 'srv web', None)
        expected = '192.168.1.1\tserver\tsrv web\n'
        self.assertEqual(expected, str(host))

    def test_str_with_comments(self):
        """Test __str__ method with comments."""
        host = Host('10.0.0.1', 'gateway', None, 'main router')
        expected = '10.0.0.1\tgateway\t\tmain router\n'
        self.assertEqual(expected, str(host))

    def test_str_with_all_fields(self):
        """Test __str__ method with all fields."""
        host = Host('172.16.0.1', 'router', 'gw gateway', 'production')
        expected = '172.16.0.1\trouter\tgw gateway\tproduction\n'
        self.assertEqual(expected, str(host))

    def test_equality_same_hosts(self):
        """Test equality for identical hosts."""
        host1 = Host('192.168.1.1', 'server', 'srv', None)
        host2 = Host('192.168.1.1', 'server', 'srv', None)
        self.assertEqual(host1, host2)

    def test_equality_different_ip(self):
        """Test inequality when IP addresses differ."""
        host1 = Host('192.168.1.1', 'server', 'srv', None)
        host2 = Host('192.168.1.2', 'server', 'srv', None)
        self.assertNotEqual(host1, host2)

    def test_equality_different_hostname(self):
        """Test inequality when hostnames differ."""
        host1 = Host('192.168.1.1', 'server1', 'srv', None)
        host2 = Host('192.168.1.1', 'server2', 'srv', None)
        self.assertNotEqual(host1, host2)

    def test_equality_different_aliases(self):
        """Test inequality when aliases differ."""
        host1 = Host('192.168.1.1', 'server', 'srv', None)
        host2 = Host('192.168.1.1', 'server', 'web', None)
        self.assertNotEqual(host1, host2)

    def test_equality_same_with_none_aliases(self):
        """Test equality when both hosts have None aliases."""
        host1 = Host('10.0.0.1', 'gateway', None, None)
        host2 = Host('10.0.0.1', 'gateway', None, None)
        self.assertEqual(host1, host2)

    def test_equality_ignores_comments(self):
        """Test that equality comparison ignores comments."""
        host1 = Host('192.168.1.1', 'server', 'srv', 'comment1')
        host2 = Host('192.168.1.1', 'server', 'srv', 'comment2')
        self.assertEqual(host1, host2)

    def test_bool_true_with_all_fields(self):
        """Test __bool__ returns True when all fields are set."""
        host = Host('192.168.1.1', 'server', 'srv', 'comment')
        self.assertTrue(bool(host))

    def test_bool_true_with_minimal_fields(self):
        """Test __bool__ returns True with just IP and hostname."""
        host = Host('127.0.0.1', 'localhost', None, None)
        self.assertTrue(bool(host))
