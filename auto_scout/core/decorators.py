"""Decorators for scan registration."""

from typing import Type

from auto_scout.core.registry import ScanRegistry
from auto_scout.core.scan import Scan


def register_scan(scan_class: Type[Scan]) -> Type[Scan]:
    """
    Decorator to auto-register scans with the ScanRegistry.

    Usage:
        @register_scan
        class MyScan(Scan):
            name = "my_scan"
            ...

    Args:
        scan_class: The Scan subclass to register

    Returns:
        The same scan class (unchanged)
    """
    ScanRegistry.register(scan_class)
    return scan_class
