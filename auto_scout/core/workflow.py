"""Base class for scan workflows."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from auto_scout.core.context import ScanContext
from auto_scout.core.executor import ScanExecutor
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan

logger = logging.getLogger(__name__)


class Workflow(ABC):
    """Base class for scan workflows."""

    def __init__(self, target: str, output_dir: str | Path = "./output") -> None:
        """
        Initialize the workflow.

        Args:
            target: Target IP address or hostname
            output_dir: Directory to store scan results
        """
        self.context = ScanContext(target_ip=target, output_dir=Path(output_dir))
        self.executor = ScanExecutor()
        logger.info(f"Initialized workflow for target: {target}")

    @abstractmethod
    async def define(self) -> None:
        """
        Define the workflow logic.

        Subclasses must implement this method to specify:
        - Which scans to run
        - In what order
        - Under what conditions
        - Whether to run in parallel or sequentially
        """
        pass

    async def run(self) -> ScanContext:
        """
        Execute the workflow.

        Returns:
            The ScanContext with all results
        """
        logger.info("Starting workflow execution...")
        try:
            await self.define()
            logger.info("Workflow completed successfully")
        except Exception as e:
            logger.error(f"Workflow failed with error: {e}", exc_info=True)
            raise
        return self.context

    async def execute_scan(self, scan: Scan) -> ScanResult:
        """
        Execute a single scan.

        Args:
            scan: The scan to execute

        Returns:
            ScanResult from the execution
        """
        return await self.executor.execute(scan, self.context)

    async def execute_parallel(self, scans: list[Scan]) -> list[ScanResult]:
        """
        Execute multiple scans in parallel.

        Args:
            scans: List of scans to execute concurrently

        Returns:
            List of ScanResults
        """
        return await self.executor.execute_parallel(scans, self.context)

    async def execute_if(self, condition: bool, scan: Scan) -> ScanResult | None:
        """
        Conditionally execute a scan.

        Args:
            condition: If True, execute the scan
            scan: The scan to execute

        Returns:
            ScanResult if executed, None if skipped
        """
        if condition:
            return await self.execute_scan(scan)
        logger.debug(f"Skipping scan '{scan.name}' (condition not met)")
        return None
