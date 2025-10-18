# Copilot Instructions for pyhosts

## Project Overview

pyhosts is a Python library for managing hosts files (e.g., `/etc/hosts`) in a Pythonic way. It provides a platform-independent interface for reading, modifying, and persisting hosts file entries using Python objects.

### Key Features
- Platform-independent (Linux, macOS, Windows)
- Object-oriented interface for hosts entries
- Support for IP addresses (IPv4 and IPv6), hostnames, aliases, and comments
- Uses `netaddr` library for IP address handling

## Architecture

The project consists of two main classes:
- `Hosts`: Main class for managing the hosts file, provides iteration and attribute-based access
- `Host`: Represents a single host entry with IP address, hostname, aliases, and comments

## Coding Standards

### Python Version
- Minimum Python 3.8
- Code should be compatible with Python 3.8 through 3.12

### Code Style
- Follow PEP 8 guidelines
- Maximum line length: 120 characters
- Use `pycodestyle pyhosts/ --max-line-length=120` to check style compliance

### Dependencies
- Core dependency: `netaddr>=0.10.0`
- Test dependencies: `pytest>=7.0.0`, `pytest-cov>=4.0.0`, `pylint>=3.0.0`, `pycodestyle>=2.11.0`

## Testing

### Running Tests
```bash
pytest test/
```

### Test Structure
- Tests are located in the `test/` directory
- Test files follow the pattern `test_*.py`
- Test classes follow the pattern `Test*`
- Test functions follow the pattern `test_*`
- Configuration is in `pytest.ini`

### Test Requirements
- All new features should include tests
- Maintain existing test coverage
- Tests should be compatible with pytest 7.0.0+

## Build and Lint Process

### Linting
```bash
pycodestyle pyhosts/ --max-line-length=120
```

### Installation
```bash
pip install -e .
```

## Common Development Tasks

### Adding a New Feature
1. Implement the feature in the appropriate module (`pyhosts/__init__.py` or `pyhosts/host.py`)
2. Add tests in `test/test_base.py` or create a new test file
3. Run tests: `pytest test/`
4. Check code style: `pycodestyle pyhosts/ --max-line-length=120`
5. Update documentation if needed

### Working with Host Entries
- Each `Host` object has: `ipaddress` (IPAddress), `hostname` (str), `aliases` (list or None), `comments` (str or None)
- The `Hosts` class provides iteration and attribute-based access to entries
- Host entries can be accessed by hostname, alias, or IP address

### Platform Considerations
- Linux/macOS hosts file: `/etc/hosts`
- Windows hosts file: `c:/windows/system32/drivers/etc/hosts`
- Platform detection is handled automatically

## Best Practices

### Code Changes
- Keep changes minimal and focused
- Maintain backward compatibility
- Follow existing code patterns and conventions
- Use meaningful variable and function names
- Add docstrings for new public methods

### Error Handling
- Use custom exceptions: `PlatformNotSupportedException`, `DuplicateEntryError`
- Handle `AddrFormatError` from netaddr for invalid IP addresses
- Provide clear error messages

### Testing
- Test edge cases (empty files, invalid entries, comments)
- Test all supported platforms if possible
- Ensure tests are isolated and repeatable

## Documentation

- Update README.md for user-facing changes
- Keep inline comments minimal unless explaining complex logic
- Update docstrings when modifying function signatures or behavior

## CI/CD

- Travis CI is configured (`.travis.yml`)
- CodeQL is enabled for security analysis (`.github/workflows/codeql.yml`)
- All tests must pass before merging
