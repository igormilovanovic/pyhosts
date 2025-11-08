"""Platform-specific path resolution for hosts files."""

import platform
from abc import ABC, abstractmethod
from pathlib import Path


class PlatformNotSupportedError(Exception):
    """Raised when the current platform is not supported."""
    pass


class PlatformResolver(ABC):
    """Abstract base class for platform-specific hosts file path resolution."""

    @abstractmethod
    def get_hosts_path(self) -> Path:
        """Get the path to the hosts file for this platform.

        Returns:
            Path object pointing to the hosts file
        """
        pass


class UnixResolver(PlatformResolver):
    """Resolver for Unix-like systems (Linux, macOS)."""

    def get_hosts_path(self) -> Path:
        """Get the path to the hosts file on Unix systems.

        Returns:
            Path to /etc/hosts
        """
        return Path('/etc') / 'hosts'


class WindowsResolver(PlatformResolver):
    """Resolver for Windows systems."""

    def get_hosts_path(self) -> Path:
        """Get the path to the hosts file on Windows.

        Returns:
            Path to C:\\Windows\\System32\\drivers\\etc\\hosts
        """
        return Path('C:/') / 'Windows' / 'System32' / 'drivers' / 'etc' / 'hosts'


class PlatformResolverFactory:
    """Factory for creating platform-specific resolvers."""

    @staticmethod
    def create() -> PlatformResolver:
        """Create a resolver for the current platform.

        Returns:
            Platform-specific resolver instance

        Raises:
            PlatformNotSupportedError: If the current platform is not supported
        """
        system = platform.system()

        if system in ('Linux', 'Darwin'):
            return UnixResolver()
        elif system == 'Windows':
            return WindowsResolver()
        else:
            raise PlatformNotSupportedError(
                f"Platform '{system}' is not supported. "
                f"Supported platforms: Linux, Darwin (macOS), Windows"
            )
