"""Tests for scan registry."""

from datetime import datetime

from auto_scout.core.context import ScanContext
from auto_scout.core.decorators import register_scan
from auto_scout.core.registry import ScanRegistry
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan


def test_scan_registration() -> None:
    """Test registering a scan."""
    # Clear registry
    ScanRegistry.clear()

    @register_scan
    class TestScan(Scan):
        @property
        def name(self) -> str:
            return "test_scan"

        async def execute(self, ctx: ScanContext) -> ScanResult:
            start = datetime.now()
            return ScanResult(
                scan_name=self.name,
                success=True,
                start_time=start,
                end_time=datetime.now(),
                raw_output="",
                parsed_data={},
            )

    assert "test_scan" in ScanRegistry.all()
    assert ScanRegistry.get("test_scan") == TestScan


def test_scan_list_names() -> None:
    """Test listing scan names."""
    ScanRegistry.clear()

    @register_scan
    class Scan1(Scan):
        @property
        def name(self) -> str:
            return "scan1"

        async def execute(self, ctx: ScanContext) -> ScanResult:
            start = datetime.now()
            return ScanResult(
                scan_name=self.name,
                success=True,
                start_time=start,
                end_time=datetime.now(),
                raw_output="",
                parsed_data={},
            )

    @register_scan
    class Scan2(Scan):
        @property
        def name(self) -> str:
            return "scan2"

        async def execute(self, ctx: ScanContext) -> ScanResult:
            start = datetime.now()
            return ScanResult(
                scan_name=self.name,
                success=True,
                start_time=start,
                end_time=datetime.now(),
                raw_output="",
                parsed_data={},
            )

    names = ScanRegistry.list_names()
    assert "scan1" in names
    assert "scan2" in names
