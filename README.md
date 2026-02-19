# pyhosts

[![CI](https://github.com/igormilovanovic/pyhosts/actions/workflows/build.yml/badge.svg)](https://github.com/igormilovanovic/pyhosts/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/pyhosts)](https://pypi.org/project/pyhosts/)
[![Python](https://img.shields.io/pypi/pyversions/pyhosts)](https://pypi.org/project/pyhosts/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
Manage system hosts files (`/etc/hosts`) the Pythonic way.

- **Platform independent** — Linux, macOS, Windows
- **Zero dependencies** — uses Python standard library only
- **Type-safe** — full type hints, `py.typed`, strict mypy
- **Immutable models** — frozen dataclasses for safety
- **List-like API** — implements `MutableSequence` protocol
- **Lazy loading** — file is read only when accessed

## Installation

```bash
pip install pyhosts
```

## Quick Start

```python
from pyhosts import Hosts

# Load the system hosts file
hosts = Hosts()

# Iterate over entries
for host in hosts:
    print(f"{host.ip_address}  {host.hostname}")

# Attribute-style access
localhost = hosts.localhost
print(localhost.ip_address)  # IPv4Address('127.0.0.1')

# Check membership
if "localhost" in hosts:
    print("found!")
```

## Usage

### Search

```python
# Find all entries matching IP, hostname, or alias
results = hosts.find("192.168.1.1")
results = hosts.find("localhost")

# Find first match
host = hosts.find_one("localhost")
```

### Add and Remove

```python
from pyhosts import Host
from ipaddress import ip_address

# Create a new entry
entry = Host(
    ip_address=ip_address("192.168.1.100"),
    hostname="myserver",
    aliases=("server", "web"),
    comment="Production server",
)

# Add it
hosts.add(entry)

# Remove by query
count = hosts.remove("myserver")
```

### Save

```python
# Save changes to disk
hosts.save()

# Save with automatic backup
hosts.save(backup=True)
```

### List-style Access

```python
# Index, slice, len, in — it's a MutableSequence
first = hosts[0]
total = len(hosts)
hosts[0] = new_entry
del hosts[2]
```

## API Reference

### `Hosts`

The main class for managing the hosts file.

| Method | Description |
|--------|-------------|
| `load()` | Load entries from hosts file |
| `save(backup=False, write_header=True)` | Save entries to hosts file |
| `find(query)` | Find all entries matching query (IP, hostname, or alias) |
| `find_one(query)` | Find first matching entry |
| `add(host, allow_duplicates=False)` | Add a new entry |
| `remove(query)` | Remove all entries matching query, returns count |

Supports full `MutableSequence` interface: indexing, slicing, iteration, `len()`, `in`, `del`.

### `Host`

Immutable (frozen) dataclass representing a single hosts file entry.

| Attribute | Type | Description |
|-----------|------|-------------|
| `ip_address` | `IPv4Address \| IPv6Address` | IP address |
| `hostname` | `str` | Primary hostname |
| `aliases` | `tuple[str, ...]` | Alias hostnames |
| `comment` | `str \| None` | Inline comment |

| Method | Description |
|--------|-------------|
| `Host.from_line(line)` | Parse a hosts file line |
| `to_line()` | Format as hosts file line |
| `matches(query)` | Check if entry matches query |
| `all_names` | Property: hostname + aliases |

### Exceptions

| Exception | Description |
|-----------|-------------|
| `DuplicateEntryError` | Raised when adding a duplicate entry |
| `PlatformNotSupportedError` | Raised on unsupported platforms |

## Requirements

- Python 3.10+
- No external dependencies

## Development

```bash
# Clone and install
git clone https://github.com/igormilovanovic/pyhosts.git
cd pyhosts
pip install -e .
pip install -r test-requirements.txt

# Run tests
pytest test/ -v

# Run tests with coverage
pytest test/ -v --cov=pyhosts

# Lint
pycodestyle pyhosts/ --max-line-length=120
```

## License

[MIT](LICENSE)
