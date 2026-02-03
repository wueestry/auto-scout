"""Scan registry for managing available scans."""

import importlib.util
import logging
import sys
from pathlib import Path
from typing import Type

from auto_scout.core.scan import Scan

logger = logging.getLogger(__name__)


class ScanRegistry:
    """Registry for all available scans."""

    _scans: dict[str, Type[Scan]] = {}

    @classmethod
    def register(cls, scan_class: Type[Scan]) -> Type[Scan]:
        """
        Register a scan class.

        Args:
            scan_class: The Scan subclass to register

        Returns:
            The scan class (for use as a decorator)
        """
        # Get the name from an instance property
        try:
            # Create a temporary instance to get the name
            temp_instance = scan_class()
            scan_name = temp_instance.name
        except Exception as e:
            logger.error(f"Failed to register scan {scan_class.__name__}: {e}")
            return scan_class

        if scan_name in cls._scans:
            logger.warning(f"Scan '{scan_name}' is already registered, overwriting")

        cls._scans[scan_name] = scan_class
        logger.debug(f"Registered scan: {scan_name}")
        return scan_class

    @classmethod
    def unregister(cls, scan_name: str) -> None:
        """Unregister a scan by name."""
        if scan_name in cls._scans:
            del cls._scans[scan_name]
            logger.debug(f"Unregistered scan: {scan_name}")

    @classmethod
    def get(cls, name: str) -> Type[Scan] | None:
        """
        Get a scan class by name.

        Args:
            name: The unique scan name

        Returns:
            The Scan class or None if not found
        """
        return cls._scans.get(name)

    @classmethod
    def all(cls) -> dict[str, Type[Scan]]:
        """
        Get all registered scans.

        Returns:
            Dictionary mapping scan names to scan classes
        """
        return cls._scans.copy()

    @classmethod
    def list_names(cls) -> list[str]:
        """Get list of all registered scan names."""
        return sorted(cls._scans.keys())

    @classmethod
    def discover(cls, directory: str | Path) -> None:
        """
        Auto-discover scans in a directory.

        Imports all .py files in the directory. Scans with @register_scan
        decorator will automatically register themselves.

        Args:
            directory: Path to directory containing scan modules
        """
        scan_dir = Path(directory)
        if not scan_dir.exists():
            logger.warning(f"Scan directory does not exist: {scan_dir}")
            return

        if not scan_dir.is_dir():
            logger.warning(f"Path is not a directory: {scan_dir}")
            return

        logger.info(f"Discovering scans in: {scan_dir}")

        # Find all .py files
        py_files = list(scan_dir.rglob("*.py"))
        logger.debug(f"Found {len(py_files)} Python files")

        for py_file in py_files:
            # Skip __init__.py and __pycache__
            if py_file.name.startswith("__"):
                continue

            try:
                # Create module name from file path
                module_name = f"auto_scout.user_scans.{py_file.stem}"

                # Load the module
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    logger.debug(f"Loaded module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to load {py_file}: {e}", exc_info=True)

        logger.info(f"Discovery complete. Registered {len(cls._scans)} scans total")

    @classmethod
    def clear(cls) -> None:
        """Clear all registered scans (useful for testing)."""
        cls._scans.clear()
