"""Example custom workflow for user extension."""

import logging

from auto_scout.core.workflow import Workflow
from auto_scout.scans.nmap import QuickNmapScan, DetailedNmapScan

logger = logging.getLogger(__name__)


class ExampleCustomWorkflow(Workflow):
    """
    Example custom workflow demonstrating how users can create workflows.

    This shows how to:
    - Extend the Workflow base class
    - Define custom scanning logic
    - Use conditional execution
    - Run scans in parallel or sequentially
    """

    async def define(self) -> None:
        """Define your custom workflow logic here."""
        logger.info("Starting example custom workflow")

        # Stage 1: Run quick scan
        logger.info("Running quick port scan...")
        await self.execute_scan(QuickNmapScan())

        # Check results and decide next steps
        if not self.context.has_open_ports():
            logger.info("No ports found, stopping workflow")
            return

        open_ports = self.context.get_open_ports()
        logger.info(f"Found {len(open_ports)} open ports")

        # Stage 2: Conditional detailed scan
        if len(open_ports) > 5:
            logger.info("Many ports found, running detailed scan...")
            await self.execute_scan(DetailedNmapScan())

        # Stage 3: Custom logic based on services
        services = self.context.get_services()
        web_ports = [p for p, s in services.items() if "http" in s.lower()]

        if web_ports:
            logger.info(f"Found web services on ports: {web_ports}")
            # Here you could add custom web enumeration scans

        logger.info("Custom workflow complete!")
