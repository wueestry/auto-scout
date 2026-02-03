"""Scan result data structures."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ScanResult:
    """Result from a scan execution."""

    scan_name: str
    success: bool
    start_time: datetime
    end_time: datetime
    raw_output: str
    parsed_data: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Get scan duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for storage."""
        return {
            "scan_name": self.scan_name,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "raw_output": self.raw_output,
            "parsed_data": self.parsed_data,
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScanResult":
        """Deserialize from dictionary."""
        return cls(
            scan_name=data["scan_name"],
            success=data["success"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            raw_output=data["raw_output"],
            parsed_data=data["parsed_data"],
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )
