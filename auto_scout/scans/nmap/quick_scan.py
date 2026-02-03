"""Quick Nmap port discovery scan."""

import logging
from datetime import datetime

from auto_scout.core.context import ScanContext
from auto_scout.core.decorators import register_scan
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan
from auto_scout.parsers.nmap import NmapParser

logger = logging.getLogger(__name__)


@register_scan
class QuickNmapScan(Scan):
    """Fast TCP port discovery scan using Nmap."""

    @property
    def name(self) -> str:
        return "quick_nmap"

    @property
    def description(self) -> str:
        return "Fast TCP SYN scan of all ports (1-65535)"

    @property
    def timeout(self) -> int:
        return 600  # 10 minutes

    @property
    def requires_root(self) -> bool:
        return True  # SYN scan requires root

    async def execute(self, ctx: ScanContext) -> ScanResult:
        """Execute the quick Nmap scan."""
        start_time = datetime.now()

        # Prepare output files
        output_dir = ctx.output_dir
        output_txt = output_dir / "nmap_quick.txt"
        output_xml = output_dir / "nmap_quick.xml"

        # Build command
        command = [
            "sudo",
            "nmap",
            "-sS",  # TCP SYN scan
            "-Pn",  # Skip ping (assume host is up)
            "-p-",  # All ports
            "--max-retries",
            "3",
            "--min-rate",
            "1000",  # Speed up scan
            "-oN",
            str(output_txt),
            "-oX",
            str(output_xml),
            ctx.target_ip,
        ]

        logger.info(f"Running quick Nmap scan on {ctx.target_ip}")
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

            # Check if we got any results
            if not parsed_data.get("hosts"):
                logger.warning("No hosts found in Nmap output")

            port_count = len(parsed_data.get("ports", []))
            logger.info(f"Quick scan complete: found {port_count} open ports")

            return self._create_result(
                success=True,
                start_time=start_time,
                end_time=end_time,
                raw_output=stdout,
                parsed_data=parsed_data,
                metadata={
                    "port_count": port_count,
                    "output_txt": str(output_txt),
                    "output_xml": str(output_xml),
                },
            )

        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Error executing quick Nmap scan: {e}", exc_info=True)

            return self._create_result(
                success=False,
                start_time=start_time,
                end_time=end_time,
                raw_output="",
                parsed_data=None,
                error=str(e),
            )
