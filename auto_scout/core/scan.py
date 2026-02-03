"""Base class for all scans."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from auto_scout.core.context import ScanContext
from auto_scout.core.result import ScanResult

logger = logging.getLogger(__name__)


class Scan(ABC):
    """Base class for all scans."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this scan."""
        pass

    @property
    def description(self) -> str:
        """Human-readable description of what this scan does."""
        return ""

    @property
    def timeout(self) -> int:
        """Timeout in seconds (default: 300)."""
        return 300

    @property
    def requires_root(self) -> bool:
        """Whether this scan requires root/sudo privileges."""
        return False

    async def can_run(self, ctx: ScanContext) -> bool:
        """
        Determine if this scan should run based on context.

        Override this method to add conditional logic.
        """
        return True

    @abstractmethod
    async def execute(self, ctx: ScanContext) -> ScanResult:
        """
        Execute the scan and return results.

        This is the main method that subclasses must implement.
        """
        pass

    async def parse(self, raw_output: str, ctx: ScanContext) -> Any:
        """
        Parse raw command output into structured data.

        Override this method to provide custom parsing logic.
        Default implementation returns raw output.
        """
        return raw_output

    async def _run_command(
        self, command: str | list[str], cwd: Path | None = None
    ) -> tuple[str, str, int]:
        """
        Run a shell command asynchronously.

        Args:
            command: Command string or list of arguments
            cwd: Working directory

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        if isinstance(command, str):
            # Split command string into list
            cmd_list = command.split()
        else:
            cmd_list = command

        logger.debug(f"Running command: {' '.join(cmd_list)}")

        process = await asyncio.create_subprocess_exec(
            *cmd_list,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", errors="ignore"),
            stderr.decode("utf-8", errors="ignore"),
            process.returncode or 0,
        )

    def _create_result(
        self,
        success: bool,
        start_time: datetime,
        end_time: datetime,
        raw_output: str,
        parsed_data: Any,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ScanResult:
        """Helper method to create a ScanResult."""
        return ScanResult(
            scan_name=self.name,
            success=success,
            start_time=start_time,
            end_time=end_time,
            raw_output=raw_output,
            parsed_data=parsed_data,
            error=error,
            metadata=metadata or {},
        )
