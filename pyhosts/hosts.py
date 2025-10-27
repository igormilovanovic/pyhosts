"""Main Hosts class for managing hosts file entries."""

import logging
from collections.abc import MutableSequence
from pathlib import Path
from typing import List, Optional, Union

from .models import Host
from .parser import HostsFileParser
from .platform_resolver import PlatformResolverFactory

logger = logging.getLogger(__name__)


class DuplicateEntryError(Exception):
    """Raised when attempting to add a duplicate host entry."""
    pass


class Hosts(MutableSequence):
    """Manages hosts file entries as a mutable sequence.

    This class provides a Pythonic interface to the system hosts file,
    implementing the MutableSequence protocol and providing lazy loading,
    searching, and persistence capabilities.

    Attributes:
        file_path: Path to the hosts file
    """

    def __init__(self, file_path: Optional[Path] = None):
        """Initialize the Hosts manager.

        Args:
            file_path: Optional custom path to hosts file.
                      If not provided, uses platform default.
        """
        if file_path is None:
            resolver = PlatformResolverFactory.create()
            self.file_path = resolver.get_hosts_path()
        else:
            self.file_path = Path(file_path) if not isinstance(file_path, Path) else file_path

        self._hosts: Optional[List[Host]] = None
        self._loaded = False

        logger.debug(f"Initialized Hosts manager for {self.file_path}")

    def _ensure_loaded(self) -> None:
        """Ensure hosts data is loaded from file."""
        if not self._loaded:
            self.load()

    def load(self) -> None:
        """Load hosts from the file.

        This method reads the hosts file and populates the internal list.
        It can be called multiple times to reload the file.
        """
        logger.debug(f"Loading hosts from {self.file_path}")
        try:
            self._hosts = HostsFileParser.parse(self.file_path)
            self._loaded = True
            logger.info(f"Loaded {len(self._hosts)} host entries from {self.file_path}")
        except FileNotFoundError:
            logger.warning(f"Hosts file not found: {self.file_path}, initializing empty list")
            self._hosts = []
            self._loaded = True
        except Exception as e:
            logger.error(f"Error loading hosts file: {e}")
            raise

    def save(self, backup: bool = False, write_header: bool = True) -> None:
        """Save the current hosts to the file.

        Args:
            backup: If True, create a backup of the original file before writing
            write_header: If True, add a header comment to identify the file as managed by pyhosts

        Raises:
            IOError: If file cannot be written
        """
        self._ensure_loaded()
        logger.debug(f"Saving {len(self._hosts)} hosts to {self.file_path}")
        HostsFileParser.write(self.file_path, self._hosts, backup=backup,
                              write_header=write_header)
        logger.info(f"Saved hosts to {self.file_path}")

    def find(self, query: str) -> List[Host]:
        """Find all hosts matching a query.

        Args:
            query: Search query (IP address, hostname, or alias)

        Returns:
            List of matching Host objects
        """
        self._ensure_loaded()
        return [host for host in self._hosts if host.matches(query)]

    def find_one(self, query: str) -> Optional[Host]:
        """Find the first host matching a query.

        Args:
            query: Search query (IP address, hostname, or alias)

        Returns:
            First matching Host object, or None if not found
        """
        results = self.find(query)
        return results[0] if results else None

    def add(self, host: Host, allow_duplicates: bool = False) -> None:
        """Add a new host entry.

        Args:
            host: Host object to add
            allow_duplicates: If False, raise error if duplicate exists

        Raises:
            DuplicateEntryError: If host already exists and allow_duplicates is False
        """
        self._ensure_loaded()

        if not allow_duplicates:
            # Check for duplicates by hostname or IP
            for existing in self._hosts:
                if (
                    existing.hostname == host.hostname or
                    existing.ip_address == host.ip_address or
                    set(existing.all_names) & set(host.all_names)
                ):
                    raise DuplicateEntryError(
                        f"Host entry conflicts with existing entry: {existing}"
                    )

        self._hosts.append(host)
        logger.debug(f"Added host: {host}")

    def remove(self, query: str) -> int:
        """Remove all hosts matching a query.

        Args:
            query: Search query (IP address, hostname, or alias)

        Returns:
            Number of hosts removed
        """
        self._ensure_loaded()
        to_remove = self.find(query)
        count = 0

        for host in to_remove:
            self._hosts.remove(host)
            count += 1
            logger.debug(f"Removed host: {host}")

        logger.info(f"Removed {count} host(s) matching query: {query}")
        return count

    # MutableSequence implementation

    def __len__(self) -> int:
        """Return the number of host entries."""
        self._ensure_loaded()
        return len(self._hosts)

    def __getitem__(self, index: Union[int, slice]) -> Union[Host, List[Host]]:
        """Get host(s) by index or slice."""
        self._ensure_loaded()
        return self._hosts[index]

    def __setitem__(self, index: Union[int, slice], value: Union[Host, List[Host]]) -> None:
        """Set host(s) by index or slice."""
        self._ensure_loaded()
        self._hosts[index] = value

    def __delitem__(self, index: Union[int, slice]) -> None:
        """Delete host(s) by index or slice."""
        self._ensure_loaded()
        del self._hosts[index]

    def insert(self, index: int, value: Host) -> None:
        """Insert a host at the specified index."""
        self._ensure_loaded()
        self._hosts.insert(index, value)

    def __contains__(self, item: Union[Host, str]) -> bool:
        """Check if a host or query matches any entry.

        Args:
            item: Either a Host object or a search query string

        Returns:
            True if item is found
        """
        self._ensure_loaded()

        if isinstance(item, Host):
            return item in self._hosts
        elif isinstance(item, str):
            return len(self.find(item)) > 0
        else:
            return False

    def __getattr__(self, name: str) -> Optional[Host]:
        """Get a host by hostname, alias, or IP address.

        This provides attribute-style access to hosts.

        Args:
            name: Hostname, alias, or IP address to search for

        Returns:
            First matching Host object, or None if not found
        """
        # Avoid infinite recursion by checking if we're accessing internal attributes
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        self._ensure_loaded()
        return self.find_one(name)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        if self._loaded:
            return f"Hosts(file_path={self.file_path!r}, entries={len(self._hosts)})"
        else:
            return f"Hosts(file_path={self.file_path!r}, not_loaded=True)"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"Hosts file: {self.file_path}"

    # Backward compatibility alias
    def persist(self, path: Optional[Path] = None) -> None:
        """Persist hosts to file (backward compatibility).

        Args:
            path: Optional path to save to. If not provided, uses self.file_path

        Deprecated: Use save() instead
        """
        if path is not None:
            original_path = self.file_path
            self.file_path = Path(path)
            try:
                self.save()
            finally:
                self.file_path = original_path
        else:
            self.save()
