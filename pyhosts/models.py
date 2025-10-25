"""Data models for pyhosts library."""

import logging
from dataclasses import dataclass
from functools import cached_property
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Host:
    """Represents a single host entry in the hosts file.

    This is an immutable dataclass representing a host entry with IP address,
    hostname, optional aliases, and optional comment.

    Attributes:
        ip_address: IPv4 or IPv6 address
        hostname: Primary hostname
        aliases: Tuple of alias names (immutable)
        comment: Optional inline comment
    """

    ip_address: IPv4Address | IPv6Address
    hostname: str
    aliases: tuple[str, ...] = ()
    comment: Optional[str] = None

    def __post_init__(self):
        """Validate the host entry after initialization."""
        if not isinstance(self.ip_address, (IPv4Address, IPv6Address)):
            raise TypeError(f"ip_address must be IPv4Address or IPv6Address, got {type(self.ip_address)}")

        if not self.hostname or not isinstance(self.hostname, str):
            raise ValueError("hostname must be a non-empty string")

        if not isinstance(self.aliases, tuple):
            raise TypeError(f"aliases must be a tuple, got {type(self.aliases)}")

        # Validate that comment doesn't contain newlines or tab characters
        if self.comment and ('\n' in self.comment or '\t' in self.comment):
            raise ValueError("comment cannot contain newlines or tab characters")

    @classmethod
    def from_line(cls, line: str) -> Optional['Host']:
        """Parse a line from the hosts file into a Host object.

        Args:
            line: A line from the hosts file

        Returns:
            Host object if line is valid, None if line should be skipped

        Raises:
            ValueError: If line is invalid
        """
        # Strip whitespace
        line = line.strip()

        # Skip empty lines
        if not line:
            return None

        # Skip comment-only lines
        if line.startswith('#'):
            return None

        # Handle inline comments
        comment = None
        if '#' in line:
            line, comment = line.split('#', 1)
            comment = comment.strip()
            line = line.strip()

        # Split the line into parts
        parts = line.split()

        if len(parts) < 2:
            logger.debug(f"Skipping invalid line (too few parts): {line}")
            return None

        # Parse IP address
        try:
            ip_addr = ip_address(parts[0])
        except ValueError as e:
            logger.debug(f"Skipping line with invalid IP address: {parts[0]} - {e}")
            return None

        # First non-IP part is hostname
        hostname = parts[1]

        # Remaining parts are aliases
        aliases = tuple(parts[2:]) if len(parts) > 2 else ()

        return cls(
            ip_address=ip_addr,
            hostname=hostname,
            aliases=aliases,
            comment=comment
        )

    def to_line(self) -> str:
        """Format the host entry as a line for the hosts file.

        Returns:
            Formatted line string with newline
        """
        # Build the line
        parts = [str(self.ip_address), self.hostname]

        # Add aliases if present
        if self.aliases:
            parts.extend(self.aliases)

        line = '\t'.join(parts)

        # Add comment if present
        if self.comment:
            line = f"{line}\t# {self.comment}"

        return line + '\n'

    @cached_property
    def all_names(self) -> tuple[str, ...]:
        """Get all names (hostname and aliases) for this host.

        Returns:
            Tuple of all names
        """
        return (self.hostname,) + self.aliases

    def matches(self, query: str) -> bool:
        """Check if this host matches a query string.

        The query can match:
        - IP address (as string)
        - Hostname
        - Any alias

        Args:
            query: Search query string

        Returns:
            True if host matches query
        """
        # Check IP address match
        if str(self.ip_address) == query:
            return True

        # Check hostname and aliases
        if query in self.all_names:
            return True

        return False

    def __str__(self) -> str:
        """String representation as a hosts file line."""
        return self.to_line().rstrip('\n')

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"Host(ip_address={self.ip_address!r}, hostname={self.hostname!r}, "
                f"aliases={self.aliases!r}, comment={self.comment!r})")
