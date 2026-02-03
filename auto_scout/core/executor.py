"""Scan execution engine with concurrency support."""

import asyncio
import logging
from datetime import datetime

from auto_scout.core.context import ScanContext
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan

logger = logging.getLogger(__name__)


class ScanExecutor:
    """Handles scan execution with timeout and concurrency support."""

    async def execute(self, scan: Scan, ctx: ScanContext) -> ScanResult:
        """
        Execute a single scan.

        Args:
            scan: The scan to execute
            ctx: The scan context

        Returns:
            ScanResult with execution details
        """
        logger.info(f"Checking if scan '{scan.name}' can run...")

        # Check if scan can run
        try:
            can_run = await scan.can_run(ctx)
            if not can_run:
                logger.info(f"Scan '{scan.name}' skipped (conditions not met)")
                return ScanResult(
                    scan_name=scan.name,
                    success=False,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    raw_output="",
                    parsed_data=None,
                    error="Scan conditions not met",
                    metadata={"skipped": True},
                )
        except Exception as e:
            logger.error(f"Error checking if scan '{scan.name}' can run: {e}")
            return self._create_error_result(scan.name, f"Error in can_run: {str(e)}")

        logger.info(f"Executing scan '{scan.name}'...")
        start_time = datetime.now()

        try:
            # Execute with timeout
            result = await asyncio.wait_for(scan.execute(ctx), timeout=scan.timeout)

            # Store result in context
            ctx.results[scan.name] = result

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            if result.success:
                logger.info(
                    f"Scan '{scan.name}' completed successfully in {duration:.2f}s"
                )
            else:
                logger.warning(
                    f"Scan '{scan.name}' completed with errors in {duration:.2f}s"
                )

            return result

        except asyncio.TimeoutError:
            end_time = datetime.now()
            logger.error(f"Scan '{scan.name}' timed out after {scan.timeout}s")
            result = ScanResult(
                scan_name=scan.name,
                success=False,
                start_time=start_time,
                end_time=end_time,
                raw_output="",
                parsed_data=None,
                error=f"Scan timed out after {scan.timeout} seconds",
                metadata={"timeout": True},
            )
            ctx.results[scan.name] = result
            return result

        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Error executing scan '{scan.name}': {e}", exc_info=True)
            result = ScanResult(
                scan_name=scan.name,
                success=False,
                start_time=start_time,
                end_time=end_time,
                raw_output="",
                parsed_data=None,
                error=str(e),
            )
            ctx.results[scan.name] = result
            return result

    async def execute_parallel(
        self, scans: list[Scan], ctx: ScanContext
    ) -> list[ScanResult]:
        """
        Execute multiple scans concurrently.

        Args:
            scans: List of scans to execute
            ctx: The scan context

        Returns:
            List of ScanResults (one per scan)
        """
        if not scans:
            return []

        logger.info(f"Executing {len(scans)} scans in parallel...")

        # Create tasks for all scans
        tasks = [self.execute(scan, ctx) for scan in scans]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions that occurred
        processed_results: list[ScanResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Scan '{scans[i].name}' raised exception: {result}",
                    exc_info=result,
                )
                error_result = self._create_error_result(scans[i].name, str(result))
                processed_results.append(error_result)
            elif isinstance(result, ScanResult):
                processed_results.append(result)

        successful = sum(1 for r in processed_results if r.success)
        logger.info(
            f"Parallel execution complete: {successful}/{len(scans)} scans successful"
        )

        return processed_results

    def _create_error_result(self, scan_name: str, error: str) -> ScanResult:
        """Create a ScanResult for an error condition."""
        now = datetime.now()
        return ScanResult(
            scan_name=scan_name,
            success=False,
            start_time=now,
            end_time=now,
            raw_output="",
            parsed_data=None,
            error=error,
        )
