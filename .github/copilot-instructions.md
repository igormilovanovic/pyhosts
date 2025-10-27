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

### File Structure

```
pyhosts/
├── __init__.py              # Package exports and version
├── hosts.py                 # Main Hosts class implementation
├── models.py                # Host model definition
├── parser.py                # Hosts file parsing logic
├── platform_resolver.py     # Platform-specific hosts file path resolution
└── py.typed                 # PEP 561 type hints marker

test/
├── __init__.py
├── test_base.py             # Basic functionality tests
└── test_new_features.py     # Tests for newer features
```

### Module Responsibilities

- **hosts.py**: Contains `Hosts` class that manages the hosts file as a mutable sequence, handles lazy loading, searching, and persistence
- **models.py**: Defines the `Host` dataclass representing a single hosts file entry
- **parser.py**: Handles parsing and formatting of hosts file content
- **platform_resolver.py**: Determines the correct hosts file path for the current platform
- **__init__.py**: Main package entry point, exports public API

## Coding Standards

### Python Version
- Minimum Python 3.10 (as specified in `pyproject.toml`)
- Code should be compatible with Python 3.10 through 3.12
- Type hints are required (project includes `py.typed` marker)

### Code Style
- Follow PEP 8 guidelines
- Maximum line length: 120 characters for pycodestyle, 100 for ruff
- Use `pycodestyle pyhosts/ --max-line-length=120` to check style compliance
- Type hints are required for all function signatures
- Use Python 3.10+ features (e.g., type union syntax with `|`, match statements)

### Dependencies
- Core dependencies: See `requirements.txt` (currently: netaddr)
- Test dependencies: See `test-requirements.txt` (pytest, pytest-cov, pycodestyle, pylint)
- Key dependency: `netaddr` for IP address handling and validation
- Type checking: Project includes type hints and `py.typed` marker
- Configuration: `pyproject.toml` contains all project metadata and tool configuration

### Tools Configuration
- **pytest**: Configured in `[tool.pytest.ini_options]` in `pyproject.toml`
- **mypy**: Type checking settings in `[tool.mypy]` in `pyproject.toml`
- **ruff**: Linting configuration in `[tool.ruff]` in `pyproject.toml`
- Line length: 100 chars (ruff), 120 chars (pycodestyle for backward compatibility)

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

### Setup for Development
```bash
# Clone the repository
git clone https://github.com/igormilovanovic/pyhosts.git
cd pyhosts

# Install in editable mode
pip install -e .

# Install test dependencies
pip install -r test-requirements.txt

# Run tests
pytest test/

# Check code style
pycodestyle pyhosts/ --max-line-length=120
```

### Adding a New Feature
1. Implement the feature in the appropriate module (`pyhosts/__init__.py`, `pyhosts/hosts.py`, or `pyhosts/models.py`)
2. Add type hints for all new functions/methods
3. Add tests in `test/test_base.py` or create a new test file like `test/test_new_features.py`
4. Run tests: `pytest test/`
5. Check code style: `pycodestyle pyhosts/ --max-line-length=120`
6. Update documentation if needed

### Example Workflows

#### Modifying Host Entry Behavior
```python
# 1. Edit pyhosts/models.py for Host model changes
# 2. Edit pyhosts/hosts.py for Hosts collection behavior
# 3. Add tests to test/test_new_features.py
# 4. Run: pytest test/test_new_features.py -v
```

#### Adding Platform Support
```python
# 1. Edit pyhosts/platform_resolver.py
# 2. Add platform detection logic
# 3. Add tests covering the new platform
# 4. Test on target platform if possible
```

#### Improving Parser
```python
# 1. Edit pyhosts/parser.py
# 2. Add tests with example hosts file content
# 3. Test with edge cases (malformed entries, comments, etc.)
```

### Working with Host Entries
- Each `Host` object is a dataclass with: `ipaddress` (IPAddress from netaddr), `hostname` (str), `aliases` (list[str] or None), `comments` (str or None)
- The `Hosts` class implements MutableSequence protocol (supports indexing, slicing, iteration, etc.)
- Host entries can be accessed by hostname, alias, or IP address using attribute-style access
- Use `Hosts.find()` to search for entries matching criteria
- Use `Hosts.find_one()` to get a single entry
- Host objects are immutable (frozen dataclass) - create new instances for modifications

### Platform Considerations
- Linux/macOS hosts file: `/etc/hosts`
- Windows hosts file: `c:/windows/system32/drivers/etc/hosts`
- Platform detection is handled automatically

## Best Practices

### API Design
- Follow the principle of least surprise - methods should do what their names suggest
- Maintain the MutableSequence interface contract for the Hosts class
- Keep Host objects immutable (frozen dataclass) for safety
- Use lazy loading to avoid unnecessary file I/O
- Provide both attribute-style and method-based access patterns

### Code Changes
- Keep changes minimal and focused
- Maintain backward compatibility
- Follow existing code patterns and conventions
- Use meaningful variable and function names
- Add docstrings for new public methods

### Error Handling
- Use custom exceptions: `PlatformNotSupportedError`, `DuplicateEntryError`
- Handle `AddrFormatError` from netaddr for invalid IP addresses
- Provide clear error messages
- All exceptions are exported from `pyhosts/__init__.py` for easy access

### Security Considerations
- This library modifies system files that require elevated permissions
- Always validate IP addresses and hostnames before adding entries
- Be cautious when persisting changes - `save()` overwrites the hosts file
- Consider backing up the hosts file before making changes in production
- Test changes in isolated environments before applying to production systems

### Performance Considerations
- The Hosts class uses lazy loading - file is only read when accessed
- Parsing happens once; subsequent access uses cached data
- For bulk operations, load once and perform multiple modifications
- Use `find()` with specific criteria rather than iterating manually
- Remember to call `save()` to persist changes - modifications are in-memory until saved

### Testing
- Test edge cases (empty files, invalid entries, comments)
- Test all supported platforms if possible
- Ensure tests are isolated and repeatable
- Use temporary files for tests that modify hosts files
- Mock file system operations when appropriate

## Troubleshooting

### Common Issues

#### Permission Denied
- **Symptom**: `PermissionError` when reading/writing hosts file
- **Solution**: Run with appropriate permissions (sudo on Linux/macOS, admin on Windows) or use a test file path
- **For Tests**: Use temporary file paths instead of system hosts file

#### Platform Not Supported
- **Symptom**: `PlatformNotSupportedError` exception
- **Solution**: Check `platform_resolver.py` for supported platforms (Linux, Darwin/macOS, Windows)

#### Invalid IP Address
- **Symptom**: `AddrFormatError` from netaddr
- **Solution**: Validate IP addresses before creating Host objects; use `netaddr.IPAddress()` for validation

#### Duplicate Entry Error
- **Symptom**: `DuplicateEntryError` when adding hosts
- **Solution**: Check existing entries with `Hosts.find()` before adding; remove duplicates first

### Debugging Tips
- Enable logging: `import logging; logging.basicConfig(level=logging.DEBUG)`
- Use `Hosts._ensure_loaded()` to explicitly trigger file loading
- Check `Hosts._loaded` flag to see if data is loaded
- Examine parsed entries with `list(hosts)` to see all entries
- Use `Host.__repr__()` for clear object representation

## Documentation

- Update README.md for user-facing changes
- Keep inline comments minimal unless explaining complex logic
- Update docstrings when modifying function signatures or behavior

## CI/CD

- Travis CI is configured (`.travis.yml`)
- CodeQL is enabled for security analysis (`.github/workflows/codeql.yml`)
- All tests must pass before merging
