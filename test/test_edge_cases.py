"""Tests for edge cases and error handling."""

import os
import tempfile
import unittest
from ipaddress import ip_address
from pathlib import Path

from pyhosts import Hosts, Host


class TestParsingEdgeCases(unittest.TestCase):
    """Test parsing edge cases in hosts files."""

    def test_empty_file(self):
        """Test parsing a completely empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(0, len(hosts))
        finally:
            temp_path.unlink()

    def test_comment_only_file(self):
        """Test parsing a file with only comments."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('# This is a comment\n')
            f.write('# Another comment\n')
            f.write('\n')
            f.write('# Yet another\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(0, len(hosts))
        finally:
            temp_path.unlink()

    def test_tabs_and_spaces_mixed(self):
        """Test parsing lines with mixed tabs and spaces."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1\t\t  localhost   local\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(1, len(hosts))
            self.assertEqual('localhost', hosts[0].hostname)
            self.assertEqual(('local',), hosts[0].aliases)
        finally:
            temp_path.unlink()

    def test_ipv6_entries(self):
        """Test parsing IPv6 host entries."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('::1 localhost6\n')
            f.write('fe80::1 link-local\n')
            f.write('2001:db8::1 example-ipv6 ipv6host\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(3, len(hosts))
            self.assertEqual(ip_address('::1'), hosts[0].ip_address)
            self.assertEqual(ip_address('fe80::1'), hosts[1].ip_address)
            self.assertEqual(('ipv6host',), hosts[2].aliases)
        finally:
            temp_path.unlink()

    def test_malformed_lines_skipped(self):
        """Test that malformed lines are silently skipped."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('not-an-ip hostname\n')
            f.write('192.168.1.1\n')  # IP only, no hostname
            f.write('127.0.0.1 valid-host\n')
            f.write('garbage line with no structure\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(1, len(hosts))
            self.assertEqual('valid-host', hosts[0].hostname)
        finally:
            temp_path.unlink()

    def test_inline_comment_parsing(self):
        """Test various inline comment formats."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('10.0.0.1 host1 # simple comment\n')
            f.write('10.0.0.2 host2 alias2 # comment with alias\n')
            f.write('10.0.0.3 host3 #no-space-comment\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(3, len(hosts))
            self.assertEqual('simple comment', hosts[0].comment)
            self.assertEqual('comment with alias', hosts[1].comment)
            self.assertEqual(('alias2',), hosts[1].aliases)
            self.assertEqual('no-space-comment', hosts[2].comment)
        finally:
            temp_path.unlink()

    def test_blank_lines_between_entries(self):
        """Test that blank lines between entries are handled."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('\n\n')
            f.write('127.0.0.1 localhost\n')
            f.write('\n')
            f.write('10.0.0.1 myhost\n')
            f.write('\n\n\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(2, len(hosts))
        finally:
            temp_path.unlink()


class TestFileHandling(unittest.TestCase):
    """Test file handling edge cases."""

    def test_nonexistent_file_creates_empty_list(self):
        """Test that a nonexistent file path results in empty hosts list."""
        temp_path = Path(tempfile.mktemp(suffix='.hosts'))
        hosts = Hosts(file_path=temp_path)
        self.assertEqual(0, len(hosts))

    def test_save_with_backup(self):
        """Test saving with backup creates a .backup file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        backup_path = temp_path.with_suffix('.backup')

        try:
            hosts = Hosts(file_path=temp_path)
            hosts.save(backup=True)

            self.assertTrue(backup_path.exists())
        finally:
            temp_path.unlink()
            if backup_path.exists():
                backup_path.unlink()

    def test_save_and_reload_preserves_data(self):
        """Test that save followed by reload preserves all entry data."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            hosts.add(Host(ip_address=ip_address('10.0.0.1'), hostname='server1',
                           aliases=('srv1', 'web1'), comment='production'))
            hosts.add(Host(ip_address=ip_address('::1'), hostname='localhost6'))
            hosts.save()

            hosts2 = Hosts(file_path=temp_path)
            self.assertEqual(2, len(hosts2))

            srv = hosts2.find_one('server1')
            self.assertIsNotNone(srv)
            self.assertEqual(('srv1', 'web1'), srv.aliases)
            self.assertEqual('production', srv.comment)

            v6 = hosts2.find_one('localhost6')
            self.assertIsNotNone(v6)
            self.assertEqual(ip_address('::1'), v6.ip_address)
        finally:
            temp_path.unlink()

    def test_save_without_header(self):
        """Test saving without pyhosts header comment."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            hosts.add(Host(ip_address=ip_address('10.0.0.1'), hostname='myhost'))
            hosts.save(write_header=False)

            with open(temp_path, 'r') as f:
                content = f.read()

            self.assertNotIn('Managed by pyhosts', content)
            self.assertIn('10.0.0.1', content)
        finally:
            temp_path.unlink()


class TestHostsOperations(unittest.TestCase):
    """Test Hosts class operations edge cases."""

    def test_remove_nonexistent_returns_zero(self):
        """Test that removing a nonexistent entry returns 0."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            count = hosts.remove('nonexistent')
            self.assertEqual(0, count)
        finally:
            temp_path.unlink()

    def test_find_by_ip_returns_multiple(self):
        """Test finding multiple entries with same IP."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('192.168.1.1 host1\n')
            f.write('192.168.1.1 host2\n')
            f.write('192.168.1.1 host3\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            results = hosts.find('192.168.1.1')
            self.assertEqual(3, len(results))
        finally:
            temp_path.unlink()

    def test_add_with_allow_duplicates(self):
        """Test adding duplicate entries with allow_duplicates=True."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            dup = Host(ip_address=ip_address('10.0.0.1'), hostname='localhost')
            hosts.add(dup, allow_duplicates=True)
            self.assertEqual(2, len(hosts))
        finally:
            temp_path.unlink()

    def test_slice_access(self):
        """Test slice access on Hosts."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('10.0.0.1 host1\n')
            f.write('10.0.0.2 host2\n')
            f.write('10.0.0.3 host3\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            sliced = hosts[0:2]
            self.assertEqual(2, len(sliced))
            self.assertEqual('host1', sliced[0].hostname)
            self.assertEqual('host2', sliced[1].hostname)
        finally:
            temp_path.unlink()

    def test_contains_with_non_string_non_host(self):
        """Test __contains__ with unexpected type returns False."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertFalse(123 in hosts)
        finally:
            temp_path.unlink()

    def test_repr_before_load(self):
        """Test repr before data is loaded."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            r = repr(hosts)
            self.assertIn('not_loaded=True', r)
        finally:
            temp_path.unlink()

    def test_repr_after_load(self):
        """Test repr after data is loaded."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            _ = len(hosts)  # trigger load
            r = repr(hosts)
            self.assertIn('entries=1', r)
        finally:
            temp_path.unlink()

    def test_str_representation(self):
        """Test str representation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertIn(str(temp_path), str(hosts))
        finally:
            temp_path.unlink()

    def test_getattr_private_raises(self):
        """Test that accessing _private attributes raises AttributeError."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            with self.assertRaises(AttributeError):
                _ = hosts._nonexistent
        finally:
            temp_path.unlink()

    def test_reload(self):
        """Test reloading the hosts file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(1, len(hosts))

            # Modify the file externally
            with open(temp_path, 'w') as f:
                f.write('127.0.0.1 localhost\n')
                f.write('10.0.0.1 newhost\n')

            hosts.load()
            self.assertEqual(2, len(hosts))
        finally:
            temp_path.unlink()


class TestFromLineEdgeCases(unittest.TestCase):
    """Test Host.from_line with edge cases."""

    def test_from_line_whitespace_only(self):
        """Test parsing whitespace-only line."""
        self.assertIsNone(Host.from_line('   \t  '))

    def test_from_line_leading_trailing_whitespace(self):
        """Test parsing line with leading/trailing whitespace."""
        host = Host.from_line('  127.0.0.1  localhost  ')
        self.assertIsNotNone(host)
        self.assertEqual('localhost', host.hostname)

    def test_from_line_multiple_spaces(self):
        """Test parsing line with multiple spaces between fields."""
        host = Host.from_line('192.168.1.1    server1    alias1    alias2')
        self.assertIsNotNone(host)
        self.assertEqual('server1', host.hostname)
        self.assertEqual(('alias1', 'alias2'), host.aliases)

    def test_from_line_tab_separated(self):
        """Test parsing tab-separated line."""
        host = Host.from_line('10.0.0.1\thost\talias')
        self.assertIsNotNone(host)
        self.assertEqual('host', host.hostname)
        self.assertEqual(('alias',), host.aliases)
