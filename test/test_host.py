import unittest
from ipaddress import ip_address

from pyhosts import Host


class TestHost(unittest.TestCase):
    """Test suite for Host class covering valid/invalid inputs, string representations, and equality checks."""

    def test_host_creation_with_ipv4(self):
        """Test creating a Host with valid IPv4 address."""
        host = Host(ip_address=ip_address('192.168.1.1'), hostname='example')
        self.assertEqual(ip_address('192.168.1.1'), host.ip_address)
        self.assertEqual('example', host.hostname)
        self.assertEqual((), host.aliases)
        self.assertIsNone(host.comment)

    def test_host_creation_with_ipv6(self):
        """Test creating a Host with valid IPv6 address."""
        host = Host(ip_address=ip_address('::1'), hostname='localhost6')
        self.assertEqual(ip_address('::1'), host.ip_address)
        self.assertEqual('localhost6', host.hostname)
        self.assertEqual((), host.aliases)
        self.assertIsNone(host.comment)

    def test_host_creation_with_aliases_tuple(self):
        """Test creating a Host with aliases as a tuple."""
        host = Host(ip_address=ip_address('127.0.0.1'), hostname='localhost', aliases=('local', 'myhost'))
        self.assertEqual(ip_address('127.0.0.1'), host.ip_address)
        self.assertEqual('localhost', host.hostname)
        self.assertEqual(('local', 'myhost'), host.aliases)
        self.assertIsNone(host.comment)

    def test_host_creation_with_single_alias(self):
        """Test creating a Host with a single alias."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='server', aliases=('srv',))
        self.assertEqual(('srv',), host.aliases)

    def test_host_creation_with_comment(self):
        """Test creating a Host with comment."""
        host = Host(ip_address=ip_address('192.168.1.100'), hostname='webserver', comment='production server')
        self.assertEqual(ip_address('192.168.1.100'), host.ip_address)
        self.assertEqual('webserver', host.hostname)
        self.assertEqual((), host.aliases)
        self.assertEqual('production server', host.comment)

    def test_host_creation_with_all_fields(self):
        """Test creating a Host with all fields populated."""
        host = Host(ip_address=ip_address('172.16.0.1'), hostname='gateway',
                    aliases=('gw', 'router'), comment='main gateway')
        self.assertEqual(ip_address('172.16.0.1'), host.ip_address)
        self.assertEqual('gateway', host.hostname)
        self.assertEqual(('gw', 'router'), host.aliases)
        self.assertEqual('main gateway', host.comment)

    def test_host_creation_with_empty_aliases_tuple(self):
        """Test creating a Host with empty tuple for aliases."""
        host = Host(ip_address=ip_address('192.168.1.1'), hostname='example', aliases=())
        self.assertEqual((), host.aliases)

    def test_invalid_ipv4_address(self):
        """Test that invalid IPv4 address raises ValueError."""
        with self.assertRaises(ValueError):
            ip_address('999.999.999.999')

    def test_invalid_ipv6_address(self):
        """Test that invalid IPv6 address raises ValueError."""
        with self.assertRaises(ValueError):
            ip_address('gggg::1')

    def test_invalid_ip_format(self):
        """Test that completely invalid IP format raises ValueError."""
        with self.assertRaises(ValueError):
            ip_address('not-an-ip')

    def test_invalid_ip_type(self):
        """Test that passing string instead of IPAddress raises TypeError."""
        with self.assertRaises(TypeError):
            Host(ip_address='192.168.1.1', hostname='invalid')

    def test_invalid_hostname_empty(self):
        """Test that empty hostname raises ValueError."""
        with self.assertRaises(ValueError):
            Host(ip_address=ip_address('192.168.1.1'), hostname='')

    def test_invalid_hostname_whitespace(self):
        """Test that whitespace-only hostname raises ValueError."""
        with self.assertRaises(ValueError):
            Host(ip_address=ip_address('192.168.1.1'), hostname='   ')

    def test_invalid_hostname_type(self):
        """Test that non-string hostname raises ValueError."""
        with self.assertRaises(ValueError):
            Host(ip_address=ip_address('192.168.1.1'), hostname=None)

    def test_invalid_aliases_type(self):
        """Test that non-tuple aliases raises TypeError."""
        with self.assertRaises(TypeError):
            Host(ip_address=ip_address('192.168.1.1'), hostname='test', aliases=['list', 'not', 'tuple'])

    def test_invalid_comment_with_newline(self):
        """Test that comment with newline raises ValueError."""
        with self.assertRaises(ValueError):
            Host(ip_address=ip_address('192.168.1.1'), hostname='test', comment='bad\ncomment')

    def test_invalid_comment_with_carriage_return(self):
        """Test that comment with carriage return raises ValueError."""
        with self.assertRaises(ValueError):
            Host(ip_address=ip_address('192.168.1.1'), hostname='test', comment='bad\rcomment')

    def test_invalid_comment_with_tab(self):
        """Test that comment with tab raises ValueError."""
        with self.assertRaises(ValueError):
            Host(ip_address=ip_address('192.168.1.1'), hostname='test', comment='bad\tcomment')

    def test_repr_minimal(self):
        """Test __repr__ method with minimal fields."""
        host = Host(ip_address=ip_address('127.0.0.1'), hostname='localhost')
        repr_str = repr(host)
        self.assertIn('127.0.0.1', repr_str)
        self.assertIn('localhost', repr_str)
        self.assertIn('ip_address', repr_str)
        self.assertIn('hostname', repr_str)

    def test_repr_with_aliases(self):
        """Test __repr__ method with aliases."""
        host = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv', 'web'))
        repr_str = repr(host)
        self.assertIn('192.168.1.1', repr_str)
        self.assertIn('server', repr_str)
        self.assertIn('srv', repr_str)
        self.assertIn('web', repr_str)

    def test_repr_with_all_fields(self):
        """Test __repr__ method with all fields."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='gateway', aliases=('gw',), comment='main router')
        repr_str = repr(host)
        self.assertIn('10.0.0.1', repr_str)
        self.assertIn('gateway', repr_str)
        self.assertIn('gw', repr_str)
        self.assertIn('main router', repr_str)

    def test_str_minimal(self):
        """Test __str__ method with minimal fields."""
        host = Host(ip_address=ip_address('127.0.0.1'), hostname='localhost')
        expected = '127.0.0.1\tlocalhost'
        self.assertEqual(expected, str(host))

    def test_str_with_aliases(self):
        """Test __str__ method with aliases."""
        host = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv', 'web'))
        expected = '192.168.1.1\tserver\tsrv\tweb'
        self.assertEqual(expected, str(host))

    def test_str_with_comment(self):
        """Test __str__ method with comment."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='gateway', comment='main router')
        expected = '10.0.0.1\tgateway\t# main router'
        self.assertEqual(expected, str(host))

    def test_str_with_all_fields(self):
        """Test __str__ method with all fields."""
        host = Host(ip_address=ip_address('172.16.0.1'), hostname='router',
                    aliases=('gw', 'gateway'), comment='production')
        expected = '172.16.0.1\trouter\tgw\tgateway\t# production'
        self.assertEqual(expected, str(host))

    def test_to_line_minimal(self):
        """Test to_line method with minimal fields."""
        host = Host(ip_address=ip_address('127.0.0.1'), hostname='localhost')
        expected = '127.0.0.1\tlocalhost\n'
        self.assertEqual(expected, host.to_line())

    def test_to_line_with_all_fields(self):
        """Test to_line method with all fields."""
        host = Host(ip_address=ip_address('172.16.0.1'), hostname='router',
                    aliases=('gw', 'gateway'), comment='production')
        expected = '172.16.0.1\trouter\tgw\tgateway\t# production\n'
        self.assertEqual(expected, host.to_line())

    def test_equality_same_hosts(self):
        """Test equality for identical hosts."""
        host1 = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv',))
        host2 = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv',))
        self.assertEqual(host1, host2)

    def test_equality_different_ip(self):
        """Test inequality when IP addresses differ."""
        host1 = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv',))
        host2 = Host(ip_address=ip_address('192.168.1.2'), hostname='server', aliases=('srv',))
        self.assertNotEqual(host1, host2)

    def test_equality_different_hostname(self):
        """Test inequality when hostnames differ."""
        host1 = Host(ip_address=ip_address('192.168.1.1'), hostname='server1', aliases=('srv',))
        host2 = Host(ip_address=ip_address('192.168.1.1'), hostname='server2', aliases=('srv',))
        self.assertNotEqual(host1, host2)

    def test_equality_different_aliases(self):
        """Test inequality when aliases differ."""
        host1 = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv',))
        host2 = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('web',))
        self.assertNotEqual(host1, host2)

    def test_equality_same_with_empty_aliases(self):
        """Test equality when both hosts have empty aliases."""
        host1 = Host(ip_address=ip_address('10.0.0.1'), hostname='gateway')
        host2 = Host(ip_address=ip_address('10.0.0.1'), hostname='gateway')
        self.assertEqual(host1, host2)

    def test_equality_includes_comment(self):
        """Test that equality comparison includes comment (dataclass default)."""
        host1 = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv',), comment='comment1')
        host2 = Host(ip_address=ip_address('192.168.1.1'), hostname='server', aliases=('srv',), comment='comment2')
        self.assertNotEqual(host1, host2)

    def test_from_line_minimal(self):
        """Test parsing minimal host line."""
        host = Host.from_line('127.0.0.1 localhost')
        self.assertEqual(ip_address('127.0.0.1'), host.ip_address)
        self.assertEqual('localhost', host.hostname)
        self.assertEqual((), host.aliases)
        self.assertIsNone(host.comment)

    def test_from_line_with_aliases(self):
        """Test parsing host line with aliases."""
        host = Host.from_line('192.168.1.1 server srv web')
        self.assertEqual(ip_address('192.168.1.1'), host.ip_address)
        self.assertEqual('server', host.hostname)
        self.assertEqual(('srv', 'web'), host.aliases)

    def test_from_line_with_comment(self):
        """Test parsing host line with comment."""
        host = Host.from_line('10.0.0.1 gateway # main router')
        self.assertEqual(ip_address('10.0.0.1'), host.ip_address)
        self.assertEqual('gateway', host.hostname)
        self.assertEqual('main router', host.comment)

    def test_from_line_empty(self):
        """Test parsing empty line returns None."""
        host = Host.from_line('')
        self.assertIsNone(host)

    def test_from_line_comment_only(self):
        """Test parsing comment-only line returns None."""
        host = Host.from_line('# this is a comment')
        self.assertIsNone(host)

    def test_from_line_invalid_ip(self):
        """Test parsing line with invalid IP returns None."""
        host = Host.from_line('not-an-ip hostname')
        self.assertIsNone(host)

    def test_from_line_too_few_parts(self):
        """Test parsing line with too few parts returns None."""
        host = Host.from_line('192.168.1.1')
        self.assertIsNone(host)

    def test_immutability(self):
        """Test that Host objects are immutable."""
        from dataclasses import FrozenInstanceError
        host = Host(ip_address=ip_address('127.0.0.1'), hostname='localhost')
        with self.assertRaises(FrozenInstanceError):
            host.hostname = 'newhost'

    def test_all_names(self):
        """Test all_names property returns hostname and aliases."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='myhost', aliases=('mh', 'host1'))
        self.assertEqual(('myhost', 'mh', 'host1'), host.all_names)

    def test_all_names_no_aliases(self):
        """Test all_names property with no aliases."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='myhost')
        self.assertEqual(('myhost',), host.all_names)

    def test_matches_by_ip(self):
        """Test matches method with IP address."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='myhost', aliases=('mh',))
        self.assertTrue(host.matches('10.0.0.1'))
        self.assertFalse(host.matches('10.0.0.2'))

    def test_matches_by_hostname(self):
        """Test matches method with hostname."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='myhost', aliases=('mh',))
        self.assertTrue(host.matches('myhost'))
        self.assertFalse(host.matches('otherhost'))

    def test_matches_by_alias(self):
        """Test matches method with alias."""
        host = Host(ip_address=ip_address('10.0.0.1'), hostname='myhost', aliases=('mh', 'host1'))
        self.assertTrue(host.matches('mh'))
        self.assertTrue(host.matches('host1'))
        self.assertFalse(host.matches('notfound'))
