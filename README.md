[![Build Status](https://travis-ci.org/igormilovanovic/pyhosts.svg?branch=master)](https://travis-ci.org/igormilovanovic/pyhosts)

pyhosts
=======

Python library for managing hosts file (eg. /etc/hosts) in a Pythonic way:
- Platform independent (Linux, macOS, Windows)
- Uses immutable Python dataclasses to represent hosts entries
- Modern, type-safe API with full type hints
- Implements MutableSequence protocol for list-like operations

Examples
========

### Basic Usage

```python
from pyhosts import Hosts

# Load the system hosts file
myhosts = Hosts()

# Iterate over all host entries
for host in myhosts:
    print(host)
# Host(ip_address=IPv4Address('127.0.0.1'), hostname='localhost', aliases=('localhost.localdomain',), comment=None)
# Host(ip_address=IPv6Address('::1'), hostname='localhost6', aliases=('localhost6.localdomain6',), comment=None)
```

### Accessing Host Entries

```python
# Access hosts by hostname (attribute-style)
host = myhosts.localhost
print(host.ip_address)  # IPv4Address('127.0.0.1')
print(host.hostname)    # 'localhost'
print(host.aliases)     # ('localhost.localdomain',)
print(host.comment)     # None

# Access by index (list-style)
first_host = myhosts[0]

# Check if a host exists
if 'localhost' in myhosts:
    print("localhost entry found")
```

### Searching for Hosts

```python
# Find all hosts matching a query (by IP, hostname, or alias)
results = myhosts.find('192.168.1.1')
results = myhosts.find('localhost')

# Find the first matching host
host = myhosts.find_one('localhost')
```

### Adding and Removing Hosts

```python
from pyhosts import Host
from ipaddress import ip_address

# Create a new host entry
new_host = Host(
    ip_address=ip_address('192.168.1.100'),
    hostname='myserver',
    aliases=('server', 'web'),
    comment='Production server'
)

# Add the host
myhosts.add(new_host)

# Remove hosts by query (returns count of removed entries)
count = myhosts.remove('myserver')
print(f"Removed {count} host(s)")
```

### Saving Changes

```python
# Save changes back to the hosts file
myhosts.save()

# Save without header comment
myhosts.save(write_header=False)

# Save with backup
myhosts.save(backup=True)
```

Requirements
============

- Python 3.10 or higher
- No external dependencies (uses standard library only)

Installation
============

```bash
pip install pyhosts
```

Or install from source:

```bash
git clone https://github.com/igormilovanovic/pyhosts.git
cd pyhosts
pip install -e .
```

Development
===========

### Running Tests

```bash
# Install development dependencies
pip install -r test-requirements.txt

# Run tests
pytest test/

# Run with coverage
pytest test/ --cov=pyhosts
```

### Code Style

```bash
# Check code style (max line length: 120)
pycodestyle pyhosts/ --max-line-length=120
```

### Project Structure

- `pyhosts/hosts.py` - Main `Hosts` class for managing hosts file
- `pyhosts/models.py` - `Host` dataclass representing individual entries
- `pyhosts/parser.py` - Parsing and writing hosts file content
- `pyhosts/platform_resolver.py` - Platform-specific hosts file location

API Reference
=============

### Hosts Class

The main class for managing the hosts file.

**Methods:**
- `load()` - Load entries from hosts file
- `save(backup=False, write_header=True)` - Save entries to hosts file
- `find(query: str)` - Find all hosts matching query (IP, hostname, or alias)
- `find_one(query: str)` - Find first host matching query
- `add(host: Host, allow_duplicates=False)` - Add a new host entry
- `remove(query: str)` - Remove all hosts matching query
- Supports list operations: indexing, slicing, iteration, `len()`, `in` operator

### Host Class

Immutable dataclass representing a single host entry.

**Attributes:**
- `ip_address` - IPv4Address or IPv6Address
- `hostname` - Primary hostname (str)
- `aliases` - Tuple of alias names
- `comment` - Optional inline comment (str)

**Methods:**
- `from_line(line: str)` - Parse a line from hosts file
- `to_line()` - Format as hosts file line
- `matches(query: str)` - Check if entry matches query
- `all_names` - Property returning all names (hostname + aliases)

### Exceptions

- `DuplicateEntryError` - Raised when adding duplicate host entry
- `PlatformNotSupportedError` - Raised on unsupported platform

Resources
=========

- [Hosts file - Wikipedia](https://en.wikipedia.org/wiki/Hosts_(file))
- [GitHub Repository](https://github.com/igormilovanovic/pyhosts)
- [Issue Tracker](https://github.com/igormilovanovic/pyhosts/issues)
