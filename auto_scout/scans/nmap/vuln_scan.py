"""Nmap vulnerability scanning using vuln scripts."""

import logging
from datetime import datetime

from auto_scout.core.context import ScanContext
from auto_scout.core.decorators import register_scan
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan
from auto_scout.parsers.nmap import NmapParser

logger = logging.getLogger(__name__)


@register_scan
class VulnNmapScan(Scan):
    """Vulnerability scanning using Nmap vuln scripts."""

    @property
    def name(self) -> str:
        return "vuln_nmap"

    @property
    def description(self) -> str:
        return "Run Nmap vulnerability detection scripts on open ports"

    @property
    def timeout(self) -> int:
        return 1800  # 30 minutes (vuln scripts can be slow)

    @property
    def requires_root(self) -> bool:
        return True

    async def can_run(self, ctx: ScanContext) -> bool:
        """Only run if we have open ports and significant services."""
        open_ports = ctx.get_open_ports()
        if not open_ports:
            logger.info("No open ports found, skipping vulnerability scan")
            return False

        # Optional: only run if we have more than a few ports
        # This makes sense for thorough pentests but not quick scans
        if len(open_ports) < 3:
            logger.info(
                "Less than 3 ports open, skipping vulnerability scan "
                "(can be overridden)"
            )
            # Allow override via metadata
            return ctx.metadata.get("force_vuln_scan", False)

        return True

    async def execute(self, ctx: ScanContext) -> ScanResult:
        """Execute the vulnerability scan."""
        start_time = datetime.now()

        # Get open ports from context
        open_ports = ctx.get_open_ports()
        ports_str = ",".join(map(str, open_ports))

        # Prepare output files
        output_dir = ctx.output_dir
        output_txt = output_dir / "nmap_vuln.txt"
        output_xml = output_dir / "nmap_vuln.xml"

        # Build command
        command = [
            "sudo",
            "nmap",
            "-p",
            ports_str,
            "--script",
            "vuln",  # Run vulnerability detection scripts
            "-oN",
            str(output_txt),
            "-oX",
            str(output_xml),
            ctx.target_ip,
        ]

        logger.info(
            f"Running vulnerability scan on {len(open_ports)} ports: {ports_str}"
        )
        logger.debug(f"Command: {' '.join(command)}")
        logger.warning("Vulnerability scan can take a long time, please be patient...")

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

            # Count ports with script results (potential vulnerabilities)
            vuln_count = sum(
                1 for port in parsed_data.get("ports", []) if port.get("scripts")
            )
            logger.info(
                f"Vulnerability scan complete: {vuln_count} ports with script output"
            )

            return self._create_result(
                success=True,
                start_time=start_time,
                end_time=end_time,
                raw_output=stdout,
                parsed_data=parsed_data,
                metadata={
                    "vuln_ports": vuln_count,
                    "scanned_ports": len(open_ports),
                    "output_txt": str(output_txt),
                    "output_xml": str(output_xml),
                },
            )

        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Error executing vulnerability scan: {e}", exc_info=True)

            return self._create_result(
                success=False,
                start_time=start_time,
                end_time=end_time,
                raw_output="",
                parsed_data=None,
                error=str(e),
            )
