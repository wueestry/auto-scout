"""Storage utilities for persisting scan results."""

import json
import logging
from pathlib import Path
from typing import Any

from auto_scout.core.context import ScanContext

logger = logging.getLogger(__name__)


class ResultStorage:
    """Handle result persistence to JSON files."""

    @staticmethod
    def save(ctx: ScanContext, filename: str = "results.json") -> Path:
        """
        Save scan context to JSON file.

        Args:
            ctx: The scan context to save
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        output_path = ctx.output_dir / filename

        try:
            data = ctx.to_dict()
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Results saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save results: {e}", exc_info=True)
            raise

    @staticmethod
    def load(file_path: str | Path) -> dict[str, Any]:
        """
        Load scan context from JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary with scan data
        """
        path = Path(file_path)

        try:
            with open(path) as f:
                data = json.load(f)

            logger.info(f"Results loaded from: {path}")
            return data

        except FileNotFoundError:
            logger.error(f"Results file not found: {path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load results: {e}", exc_info=True)
            raise

    @staticmethod
    def save_summary(ctx: ScanContext, filename: str = "summary.txt") -> Path:
        """
        Save a human-readable summary of the scan.

        Args:
            ctx: The scan context
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        output_path = ctx.output_dir / filename

        try:
            lines = []
            lines.append("=" * 70)
            lines.append("AUTO-SCOUT SCAN SUMMARY")
            lines.append("=" * 70)
            lines.append(f"\nTarget: {ctx.target_ip}")
            lines.append(f"Output Directory: {ctx.output_dir}")
            lines.append("")

            # Scan results summary
            successful = ctx.get_successful_results()
            lines.append(f"Completed Scans: {len(successful)}/{len(ctx.results)}")
            lines.append("")

            for scan_name, result in ctx.results.items():
                status = "✓" if result.success else "✗"
                lines.append(f"{status} {scan_name}: {result.duration:.2f}s")
                if result.error:
                    lines.append(f"  Error: {result.error}")

            # Port information
            open_ports = ctx.get_open_ports()
            if open_ports:
                lines.append(f"\nOpen Ports ({len(open_ports)}):")
                lines.append(f"  {', '.join(map(str, open_ports))}")

            # Service information
            services = ctx.get_services()
            if services:
                lines.append(f"\nDetected Services ({len(services)}):")
                for port, service in sorted(services.items()):
                    lines.append(f"  {port:5d} - {service}")

            lines.append("\n" + "=" * 70)

            with open(output_path, "w") as f:
                f.write("\n".join(lines))

            logger.info(f"Summary saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save summary: {e}", exc_info=True)
            raise
