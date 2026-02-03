"""Tests for core scan context functionality."""

from pathlib import Path

from auto_scout.core.context import ScanContext
from auto_scout.core.result import ScanResult
from datetime import datetime


def test_scan_context_creation() -> None:
    """Test creating a ScanContext."""
    ctx = ScanContext(target_ip="192.168.1.1", output_dir=Path("/tmp/test"))
    assert ctx.target_ip == "192.168.1.1"
    assert ctx.output_dir == Path("/tmp/test")
    assert len(ctx.results) == 0


def test_scan_context_get_open_ports() -> None:
    """Test getting open ports from context."""
    ctx = ScanContext(target_ip="192.168.1.1", output_dir=Path("/tmp/test"))

    # Add a mock result with ports
    result = ScanResult(
        scan_name="test_scan",
        success=True,
        start_time=datetime.now(),
        end_time=datetime.now(),
        raw_output="",
        parsed_data={
            "ports": [
                {"port_id": "80", "service_name": "http"},
                {"port_id": "443", "service_name": "https"},
            ]
        },
    )
    ctx.results["test_scan"] = result

    ports = ctx.get_open_ports()
    assert 80 in ports
    assert 443 in ports
    assert len(ports) == 2


def test_scan_context_get_services() -> None:
    """Test getting services from context."""
    ctx = ScanContext(target_ip="192.168.1.1", output_dir=Path("/tmp/test"))

    result = ScanResult(
        scan_name="test_scan",
        success=True,
        start_time=datetime.now(),
        end_time=datetime.now(),
        raw_output="",
        parsed_data={
            "ports": [
                {"port_id": "80", "service_name": "http"},
                {"port_id": "22", "service_name": "ssh"},
            ]
        },
    )
    ctx.results["test_scan"] = result

    services = ctx.get_services()
    assert services[80] == "http"
    assert services[22] == "ssh"
