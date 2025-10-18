import unittest
import platform
import tempfile
from pathlib import Path
from ipaddress import ip_address

from pyhosts import Hosts, Host


class TestBaseCases(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.myhosts = Hosts()

    def test_one(self):
        # Test that the file path is set correctly based on platform
        if platform.system() in ("Linux", "Darwin"):
            expected_path = Path("/etc/hosts")
        elif platform.system() == "Windows":
            expected_path = Path("C:/Windows/System32/drivers/etc/hosts")
        else:
            # This branch should not be reached since setUp would have already
            # raised PlatformNotSupportedError when creating Hosts()
            self.fail("Unexpected platform: %s" % platform.system())
        self.assertEqual(expected_path, self.myhosts.file_path)

    def test_content_empty(self):
        # Create an empty temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            temp_path = Path(f.name)
        
        try:
            hosts = Hosts(file_path=temp_path)
            entries = [i for i in hosts]
            expected = []
            self.assertEqual(expected, entries)
        finally:
            temp_path.unlink()

    def test_content_one_entry(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1\t\tlocalhost.localdomain localhost\n')
            temp_path = Path(f.name)
        
        try:
            hosts = Hosts(file_path=temp_path)
            entries = list(hosts)
            expected = [Host(ip_address=ip_address('127.0.0.1'), 
                           hostname='localhost.localdomain', 
                           aliases=('localhost',),
                           comment=None)]
            self.assertEqual(expected, entries)
        finally:
            temp_path.unlink()

    def test_content_many_entries(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('127.0.0.1\t\tlocalhost.localdomain localhost\n')
            f.write('::1\t\tlocalhost6.localdomain6 localhost6\n')
            f.write('\n')
            f.write('172.19.29.156\tigor\n')
            f.write('\n')
            f.write('# virtual machines\n')
            f.write('192.168.122.167\tmarev3\n')
            temp_path = Path(f.name)
        
        try:
            hosts = Hosts(file_path=temp_path)
            entries = [host for host in hosts]
            expected = [Host(ip_address=ip_address('127.0.0.1'), 
                           hostname='localhost.localdomain', 
                           aliases=('localhost',),
                           comment=None),
                       Host(ip_address=ip_address('::1'), 
                           hostname='localhost6.localdomain6', 
                           aliases=('localhost6',), 
                           comment=None),
                       Host(ip_address=ip_address('172.19.29.156'), 
                           hostname='igor', 
                           aliases=(), 
                           comment=None),
                       Host(ip_address=ip_address('192.168.122.167'), 
                           hostname='marev3', 
                           aliases=(), 
                           comment=None)]

            self.assertEqual(expected, entries)
        finally:
            temp_path.unlink()

    def test_read_host(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.write('1.1.1.1\tigor\n')
            temp_path = Path(f.name)
        
        try:
            hosts = Hosts(file_path=temp_path)
            self.assertEqual(ip_address('1.1.1.1'), hosts.igor.ip_address)
            self.assertEqual('igor', hosts.igor.hostname)
        finally:
            temp_path.unlink()

    def test_format_same_as_file(self):
        _readlines = ['127.0.0.1\tlocalhost.localdomain\tlocalhost\n',
                      '::1\tlocalhost6.localdomain6\tlocalhost6\n',
                      '172.19.29.156\tigor\n',
                      '192.168.122.167\tmarev3\n']
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hosts') as f:
            f.writelines(_readlines)
            temp_path = Path(f.name)
        
        try:
            hosts = Hosts(file_path=temp_path)
            entries = [host for host in hosts]

            for first, second in zip(_readlines, entries):
                # Compare the line content (strip newline from first)
                self.assertEqual(first.rstrip('\n'), str(second))
        finally:
            temp_path.unlink()
