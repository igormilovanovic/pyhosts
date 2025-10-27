"""pyhosts - Pythonic way to manage hosts files.

This library provides a modern, type-safe interface for managing system hosts files
across different platforms (Linux, macOS, Windows).
"""

import logging

from .hosts import Hosts, DuplicateEntryError
from .models import Host
from .platform_resolver import PlatformNotSupportedError

__version__ = "1.0.0"

__all__ = [
    'Hosts',
    'Host',
    'DuplicateEntryError',
    'PlatformNotSupportedError',
]

# Configure null handler for library logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
