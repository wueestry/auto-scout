"""Detailed Nmap service and version detection scan."""

import logging
from datetime import datetime

from auto_scout.core.context import ScanContext
from auto_scout.core.decorators import register_scan
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan
from auto_scout.parsers.nmap import NmapParser

logger = logging.getLogger(__name__)


@register_scan
class DetailedNmapScan(Scan):
    """Detailed service and version detection scan on open ports."""

    @property
    def name(self) -> str:
        return "detailed_nmap"

    @property
    def description(self) -> str:
        return "Service version detection and OS fingerprinting on open ports"

    @property
    def timeout(self) -> int:
        return 900  # 15 minutes

    @property
    def requires_root(self) -> bool:
        return True

    async def can_run(self, ctx: ScanContext) -> bool:
        """Only run if we have open ports from a previous scan."""
        open_ports = ctx.get_open_ports()
        if not open_ports:
            logger.info("No open ports found, skipping detailed scan")
            return False
        return True

    async def execute(self, ctx: ScanContext) -> ScanResult:
        """Execute the detailed Nmap scan."""
        start_time = datetime.now()

        # Get open ports from context
        open_ports = ctx.get_open_ports()
        ports_str = ",".join(map(str, open_ports))

        # Prepare output files
        output_dir = ctx.output_dir
        output_txt = output_dir / "nmap_detailed.txt"
        output_xml = output_dir / "nmap_detailed.xml"

        # Build command
        command = [
            "sudo",
            "nmap",
            "-sV",  # Service version detection
            "-sC",  # Default scripts
            "-A",  # OS detection, version detection, script scanning
            "-O",  # OS detection
            "-p",
            ports_str,
            "-oN",
            str(output_txt),
            "-oX",
            str(output_xml),
            ctx.target_ip,
        ]

        logger.info(
            f"Running detailed Nmap scan on {len(open_ports)} ports: {ports_str}"
        )
        logger.debug(f"Command: {' '.join(command)}")

        try:
            # Run the command
            stdout, stderr, returncode = await self._run_command(command)

            end_time = datetime.now()

            if returncode != 0:
                error_msg = f"Nmap returned non-zero exit code: {returncode}"
                logger.error(error_msg)
                if stderr:
                    logger.error(f"Stderr: {stderr}")

                return self._create_result(
                    success=False,
                    start_time=start_time,
                    end_time=end_time,
                    raw_output=stdout + "\n" + stderr,
                    parsed_data=None,
                    error=error_msg,
                )

            # Parse the XML output
            parser = NmapParser()
            parsed_data = parser.parse_file(output_xml)

            service_count = sum(
                1 for port in parsed_data.get("ports", []) if port.get("service_name")
            )
            logger.info(f"Detailed scan complete: identified {service_count} services")

            return self._create_result(
                success=True,
                start_time=start_time,
                end_time=end_time,
                raw_output=stdout,
                parsed_data=parsed_data,
                metadata={
                    "service_count": service_count,
                    "scanned_ports": len(open_ports),
                    "output_txt": str(output_txt),
                    "output_xml": str(output_xml),
                },
            )

        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Error executing detailed Nmap scan: {e}", exc_info=True)

            return self._create_result(
                success=False,
                start_time=start_time,
                end_time=end_time,
                raw_output="",
                parsed_data=None,
                error=str(e),
            )
