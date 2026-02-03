"""Example custom scan for user extension."""

from datetime import datetime

from auto_scout.core.context import ScanContext
from auto_scout.core.decorators import register_scan
from auto_scout.core.result import ScanResult
from auto_scout.core.scan import Scan


@register_scan
class ExampleCustomScan(Scan):
    """
    Example custom scan demonstrating how users can extend auto-scout.

    This scan is a template showing:
    - How to use the @register_scan decorator
    - How to implement required properties and methods
    - How to add conditional logic with can_run()
    - How to execute commands and parse results
    """

    @property
    def name(self) -> str:
        """Unique identifier for this scan."""
        return "example_custom"

    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Example custom scan (template for users)"

    @property
    def timeout(self) -> int:
        """Timeout in seconds."""
        return 120

    @property
    def requires_root(self) -> bool:
        """Whether this scan needs sudo/root privileges."""
        return False

    async def can_run(self, ctx: ScanContext) -> bool:
        """
        Decide if this scan should run based on previous results.

        Example: only run if we found specific ports or services.
        """
        # Example: only run if port 80 or 443 is open
        open_ports = ctx.get_open_ports()
        return 80 in open_ports or 443 in open_ports

    async def execute(self, ctx: ScanContext) -> ScanResult:
        """
        Execute the scan and return results.

        This is where your scan logic goes.
        """
        start_time = datetime.now()

        try:
            # Example: run a custom command
            # command = ["your", "command", "here", ctx.target_ip]
            # stdout, stderr, returncode = await self._run_command(command)

            # For this example, we'll just create a mock result
            result_data = {
                "example_field": "example_value",
                "target": ctx.target_ip,
            }

            end_time = datetime.now()

            return self._create_result(
                success=True,
                start_time=start_time,
                end_time=end_time,
                raw_output="Example output",
                parsed_data=result_data,
                metadata={"example": True},
            )

        except Exception as e:
            end_time = datetime.now()
            return self._create_result(
                success=False,
                start_time=start_time,
                end_time=end_time,
                raw_output="",
                parsed_data=None,
                error=str(e),
            )
