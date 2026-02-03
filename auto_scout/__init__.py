"""auto-scout: A reconnaissance and scanning framework for CTFs and pentesting."""

__version__ = "2.0.0"

from auto_scout.core import (
    ScanContext,
    ScanExecutor,
    ScanRegistry,
    ScanResult,
    Scan,
    Workflow,
    register_scan,
)

__all__ = [
    "ScanContext",
    "ScanExecutor",
    "ScanRegistry",
    "ScanResult",
    "Scan",
    "Workflow",
    "register_scan",
]
