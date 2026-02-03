"""Core framework components for auto-scout."""

from auto_scout.core.context import ScanContext
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan
from auto_scout.core.workflow import Workflow
from auto_scout.core.executor import ScanExecutor
from auto_scout.core.registry import ScanRegistry
from auto_scout.core.decorators import register_scan

__all__ = [
    "ScanContext",
    "ScanResult",
    "Scan",
    "Workflow",
    "ScanExecutor",
    "ScanRegistry",
    "register_scan",
]
