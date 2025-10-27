"""Parser for reading and writing hosts files."""

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import List

from .models import Host

logger = logging.getLogger(__name__)


class HostsFileParser:
    """Parser for reading and writing hosts files."""

    @staticmethod
    def parse(file_path: Path) -> List[Host]:
        """Parse a hosts file and return a list of Host objects.

        Args:
            file_path: Path to the hosts file

        Returns:
            List of Host objects

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        logger.debug(f"Parsing hosts file: {file_path}")

        hosts = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, start=1):
                    try:
                        host = Host.from_line(line)
                        if host is not None:
                            hosts.append(host)
                    except Exception as e:
                        logger.warning(f"Error parsing line {line_num} in {file_path}: {e}")
                        continue
        except FileNotFoundError:
            logger.warning(f"Hosts file not found: {file_path}")
            raise
        except IOError as e:
            logger.error(f"Error reading hosts file {file_path}: {e}")
            raise

        logger.debug(f"Parsed {len(hosts)} host entries from {file_path}")
        return hosts

    @staticmethod
    def write(file_path: Path, hosts: List[Host], backup: bool = False) -> None:
        """Write hosts to a file using atomic write operation.

        Uses a temporary file and atomic rename to ensure the write is safe.

        Args:
            file_path: Path to the hosts file
            hosts: List of Host objects to write
            backup: If True, create a backup of the original file

        Raises:
            IOError: If file cannot be written
        """
        logger.debug(f"Writing {len(hosts)} hosts to {file_path}")

        # Create backup if requested
        if backup and file_path.exists():
            backup_path = file_path.with_suffix('.backup')
            logger.debug(f"Creating backup at {backup_path}")
            try:
                shutil.copy2(file_path, backup_path)
            except IOError as e:
                logger.error(f"Failed to create backup: {e}")
                raise

        # Write to temporary file first
        temp_fd = None
        temp_path = None

        temp_path = None
        try:
            # Create temp file in same directory as target for atomic rename
            temp_fd, temp_path_str = tempfile.mkstemp(
                dir=file_path.parent,
                prefix='.pyhosts_tmp_',
                text=True
            )
            temp_path = Path(temp_path_str)

            # Close the file descriptor immediately, we'll use the path
            os.close(temp_fd)

            # Write content to temp file using the path directly
            with open(temp_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("# Managed by pyhosts\n")
                f.write("# https://github.com/igormilovanovic/pyhosts\n\n")

                # Write all host entries
                for host in hosts:
                    f.write(host.to_line())

            # Set secure permissions before copying from original
            # Default to read/write for owner and group, read for others (0o644)
            os.chmod(temp_path, 0o644)

            # Copy permissions from original file if it exists
            if file_path.exists():
                # Get the original file's permissions
                original_stat = file_path.stat()
                # Only copy if permissions are reasonably secure (not world-writable)
                if not (original_stat.st_mode & 0o002):
                    shutil.copystat(file_path, temp_path)
                else:
                    logger.warning(f"Original file has insecure permissions, using 0o644 instead")

            # Atomic rename
            temp_path.replace(file_path)
            logger.debug(f"Successfully wrote hosts file to {file_path}")

        except Exception as e:
            logger.error(f"Error writing hosts file {file_path}: {e}")
            # Clean up temp file if it exists
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise
