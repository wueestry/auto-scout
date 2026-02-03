"""Scan context for carrying state through workflows."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from auto_scout.core.result import ScanResult


@dataclass
class ScanContext:
    """Carries state and results through the workflow."""

    target_ip: str
    output_dir: Path
    results: dict[str, ScanResult] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure output_dir is a Path object."""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_result(self, scan_name: str) -> ScanResult | None:
        """Get result of a specific scan."""
        return self.results.get(scan_name)

    def has_result(self, scan_name: str) -> bool:
        """Check if a scan has been executed."""
        return scan_name in self.results

    def get_successful_results(self) -> dict[str, ScanResult]:
        """Get all successful scan results."""
        return {name: result for name, result in self.results.items() if result.success}

    def has_open_ports(self) -> bool:
        """Check if any scans found open ports."""
        for result in self.results.values():
            if result.success and result.parsed_data:
                if isinstance(result.parsed_data, dict):
                    ports = result.parsed_data.get("ports", [])
                    if ports:
                        return True
        return False

    def get_open_ports(self) -> list[int]:
        """Get list of all discovered open ports."""
        ports: set[int] = set()
        for result in self.results.values():
            if result.success and result.parsed_data:
                if isinstance(result.parsed_data, dict):
                    port_list = result.parsed_data.get("ports", [])
                    for port_info in port_list:
                        if isinstance(port_info, dict):
                            port_id = port_info.get("port_id")
                            if port_id:
                                ports.add(int(port_id))
        return sorted(ports)

    def get_services(self) -> dict[int, str]:
        """Get port to service name mapping."""
        services: dict[int, str] = {}
        for result in self.results.values():
            if result.success and result.parsed_data:
                if isinstance(result.parsed_data, dict):
                    port_list = result.parsed_data.get("ports", [])
                    for port_info in port_list:
                        if isinstance(port_info, dict):
                            port_id = port_info.get("port_id")
                            service_name = port_info.get("service_name", "unknown")
                            if port_id:
                                services[int(port_id)] = service_name
        return services

    def get_ports_by_service(self, service_pattern: str) -> list[int]:
        """Get ports running a specific service (supports partial match)."""
        services = self.get_services()
        return [
            port
            for port, service in services.items()
            if service_pattern.lower() in service.lower()
        ]

    def to_dict(self) -> dict[str, Any]:
        """Serialize context to dictionary."""
        return {
            "target_ip": self.target_ip,
            "output_dir": str(self.output_dir),
            "results": {
                name: result.to_dict() for name, result in self.results.items()
            },
            "metadata": self.metadata,
        }
