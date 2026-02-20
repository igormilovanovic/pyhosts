"""Tests for new features added in the modernization."""

import unittest
import tempfile
from dataclasses import FrozenInstanceError
from pathlib import Path
from ipaddress import ip_address

from pyhosts import Hosts, Host, DuplicateEntryError


class TestNewFeatures(unittest.TestCase):
    """Test new features added in the modernization."""

    def test_host_immutability(self):
        """Test that Host objects are immutable (frozen dataclass)."""
        host = Host(
            ip_address=ip_address('127.0.0.1'),
            hostname='localhost',
            aliases=('local',),
            comment='test'
        )

        # Should not be able to modify attributes
        with self.assertRaises(FrozenInstanceError):
            host.hostname = 'newhost'

    def test_host_from_line_with_comment(self):
        """Test parsing a line with an inline comment."""
        host = Host.from_line("192.168.1.1 server1 srv1 # my server")

        self.assertEqual(ip_address('192.168.1.1'), host.ip_address)
        self.assertEqual('server1', host.hostname)
        self.assertEqual(('srv1',), host.aliases)
        self.assertEqual('my server', host.comment)

    def test_host_matches(self):
        """Test the matches method for searching."""
        host = Host(
            ip_address=ip_address('10.0.0.1'),
            hostname='myhost',
            aliases=('mh', 'host1'),
        )

        self.assertTrue(host.matches('10.0.0.1'))
        self.assertTrue(host.matches('myhost'))
        self.assertTrue(host.matches('mh'))
        self.assertTrue(host.matches('host1'))
        self.assertFalse(host.matches('notfound'))

    def test_host_all_names(self):
        """Test the all_names cached property."""
        host = Host(
            ip_address=ip_address('10.0.0.1'),
            hostname='myhost',
            aliases=('alias1', 'alias2'),
        )

        all_names = host.all_names
        self.assertEqual(('myhost', 'alias1', 'alias2'), all_names)

    def test_hosts_lazy_loading(self):
        """Test that hosts are loaded lazily."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            # Should not be loaded yet
            self.assertFalse(hosts._loaded)

            # Access should trigger loading
            _ = len(hosts)
            self.assertTrue(hosts._loaded)
        finally:
            temp_path.unlink()

    def test_hosts_find(self):
        """Test the find method."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost local\n')
            f.write('192.168.1.1 server1\n')
            f.write('192.168.1.2 server2\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)

            # Find by hostname
            results = hosts.find('localhost')
            self.assertEqual(1, len(results))
            self.assertEqual('localhost', results[0].hostname)

            # Find by alias
            results = hosts.find('local')
            self.assertEqual(1, len(results))
            self.assertEqual('localhost', results[0].hostname)

            # Find by IP
            results = hosts.find('192.168.1.1')
            self.assertEqual(1, len(results))
            self.assertEqual('server1', results[0].hostname)

            # Not found
            results = hosts.find('notfound')
            self.assertEqual(0, len(results))
        finally:
            temp_path.unlink()

    def test_hosts_find_one(self):
        """Test the find_one method."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            f.write('192.168.1.1 server1\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)

            result = hosts.find_one('localhost')
            self.assertIsNotNone(result)
            self.assertEqual('localhost', result.hostname)

            result = hosts.find_one('notfound')
            self.assertIsNone(result)
        finally:
            temp_path.unlink()

    def test_hosts_add(self):
        """Test adding a new host."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            initial_count = len(hosts)

            new_host = Host(
                ip_address=ip_address('10.0.0.1'),
                hostname='newhost',
            )
            hosts.add(new_host)

            self.assertEqual(initial_count + 1, len(hosts))
            self.assertIn('newhost', [h.hostname for h in hosts])
        finally:
            temp_path.unlink()

    def test_hosts_add_duplicate_error(self):
        """Test that adding a duplicate hostname raises an error."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)

            duplicate_host = Host(
                ip_address=ip_address('10.0.0.1'),
                hostname='localhost',
            )

            with self.assertRaises(DuplicateEntryError):
                hosts.add(duplicate_host, allow_duplicates=False)
        finally:
            temp_path.unlink()

    def test_hosts_add_same_ip_different_hostname(self):
        """Test that same IP with different hostname is allowed."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)

            new_host = Host(
                ip_address=ip_address('127.0.0.1'),
                hostname='myapp.local',
            )
            hosts.add(new_host)
            self.assertEqual(2, len(hosts))
        finally:
            temp_path.unlink()

    def test_hosts_remove(self):
        """Test removing hosts."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            f.write('192.168.1.1 server1\n')
            f.write('192.168.1.2 server2\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            initial_count = len(hosts)

            removed = hosts.remove('server1')
            self.assertEqual(1, removed)
            self.assertEqual(initial_count - 1, len(hosts))
            self.assertIsNone(hosts.find_one('server1'))
        finally:
            temp_path.unlink()

    def test_hosts_mutable_sequence(self):
        """Test MutableSequence protocol implementation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            f.write('192.168.1.1 server1\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)

            # Test __getitem__
            first = hosts[0]
            self.assertEqual('localhost', first.hostname)

            # Test __setitem__
            new_host = Host(ip_address=ip_address('10.0.0.1'), hostname='replacement')
            hosts[0] = new_host
            self.assertEqual('replacement', hosts[0].hostname)

            # Test __delitem__
            del hosts[0]
            self.assertEqual(1, len(hosts))

            # Test insert
            hosts.insert(0, first)
            self.assertEqual('localhost', hosts[0].hostname)
        finally:
            temp_path.unlink()

    def test_hosts_contains(self):
        """Test __contains__ method."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)

            # Test with string query
            self.assertIn('localhost', hosts)
            self.assertNotIn('notfound', hosts)

            # Test with Host object
            host = hosts[0]
            self.assertIn(host, hosts)
        finally:
            temp_path.unlink()

    def test_hosts_save_and_reload(self):
        """Test saving and reloading hosts."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)

            # Add a new host
            new_host = Host(
                ip_address=ip_address('10.0.0.1'),
                hostname='newhost',
                aliases=('nh',),
                comment='test comment'
            )
            hosts.add(new_host)

            # Save
            hosts.save()

            # Reload in a new instance
            hosts2 = Hosts(file_path=temp_path)
            self.assertEqual(len(hosts), len(hosts2))

            # Verify the new host was saved
            found = hosts2.find_one('newhost')
            self.assertIsNotNone(found)
            self.assertEqual('newhost', found.hostname)
            self.assertEqual(('nh',), found.aliases)
            self.assertEqual('test comment', found.comment)
        finally:
            temp_path.unlink()

    def test_persist_backward_compatibility(self):
        """Test that persist() method still works for backward compatibility."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            hosts = Hosts(file_path=temp_path)
            new_host = Host(ip_address=ip_address('10.0.0.1'), hostname='newhost')
            hosts.add(new_host)

            # Use old persist method
            hosts.persist()

            # Verify it was saved
            hosts2 = Hosts(file_path=temp_path)
            self.assertIsNotNone(hosts2.find_one('newhost'))
        finally:
            temp_path.unlink()

    def test_context_manager_saves_on_exit(self):
        """Test that context manager auto-saves on clean exit."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            with Hosts(file_path=temp_path) as hosts:
                hosts.add(Host(ip_address=ip_address('10.0.0.1'), hostname='ctxhost'))

            # Verify it was saved automatically
            hosts2 = Hosts(file_path=temp_path)
            self.assertIsNotNone(hosts2.find_one('ctxhost'))
        finally:
            temp_path.unlink()

    def test_context_manager_no_save_on_exception(self):
        """Test that context manager does not save when an exception occurs."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1 localhost\n')
            temp_path = Path(f.name)

        try:
            try:
                with Hosts(file_path=temp_path) as hosts:
                    hosts.add(Host(ip_address=ip_address('10.0.0.1'), hostname='badhost'))
                    raise RuntimeError("something went wrong")
            except RuntimeError:
                pass

            # Verify it was NOT saved
            hosts2 = Hosts(file_path=temp_path)
            self.assertIsNone(hosts2.find_one('badhost'))
        finally:
            temp_path.unlink()
