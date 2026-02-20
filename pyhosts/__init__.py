"""pyhosts - Pythonic way to manage hosts files.

This library provides a modern, type-safe interface for managing system hosts files
across different platforms (Linux, macOS, Windows).
"""

import logging

from .hosts import DuplicateEntryError, Hosts
from .models import Host
from .platform_resolver import PlatformNotSupportedError

__version__ = "0.2.0"

__all__ = [
    'Hosts',
    'Host',
    'DuplicateEntryError',
    'PlatformNotSupportedError',
]

# Configure null handler for library logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
