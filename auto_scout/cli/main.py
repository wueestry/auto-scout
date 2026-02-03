"""Main CLI entry point for auto-scout with rich visualization."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from auto_scout.core import ScanContext
from auto_scout.core.registry import ScanRegistry
from auto_scout.utils.storage import ResultStorage
from auto_scout.workflows.pentest import PentestWorkflow

console = Console()


def print_banner() -> None:
    """Print the auto-scout banner."""
    banner = """
▄▖  ▗     ▄▖      ▗ 
▌▌▌▌▜▘▛▌▄▖▚ ▛▘▛▌▌▌▜▘
▛▌▙▌▐▖▙▌  ▄▌▙▖▙▌▙▌▐▖
    """
    console.print(
        Panel.fit(
            banner,
            title="[bold cyan]Auto-Scout[/bold cyan]",
            subtitle="[dim]Automated Reconnaissance Framework[/dim]",
            border_style="bright_blue",
        )
    )


def print_results_summary(ctx: ScanContext) -> None:
    """Print a summary of scan results using rich tables."""
    # Summary table
    summary_table = Table(title="Scan Summary", show_header=True)
    summary_table.add_column("Scan", style="cyan", no_wrap=True)
    summary_table.add_column("Status", style="magenta")
    summary_table.add_column("Duration", justify="right", style="green")
    summary_table.add_column("Details", style="yellow")

    for scan_name, result in ctx.results.items():
        status = "✓ Success" if result.success else "✗ Failed"
        status_style = "green" if result.success else "red"

        details = ""
        if result.metadata:
            port_count = result.metadata.get("port_count")
            service_count = result.metadata.get("service_count")
            if port_count is not None:
                details = f"{port_count} ports"
            elif service_count is not None:
                details = f"{service_count} services"

        summary_table.add_row(
            scan_name,
            f"[{status_style}]{status}[/{status_style}]",
            f"{result.duration:.2f}s",
            details,
        )

    console.print("\n")
    console.print(summary_table)

    # Ports table
    open_ports = ctx.get_open_ports()
    services = ctx.get_services()

    if open_ports:
        ports_table = Table(title=f"Open Ports ({len(open_ports)})", show_header=True)
        ports_table.add_column("Port", style="cyan", justify="right")
        ports_table.add_column("Protocol", style="magenta")
        ports_table.add_column("Service", style="green")

        for port in open_ports:
            service = services.get(port, "unknown")
            ports_table.add_row(str(port), "tcp", service)

        console.print("\n")
        console.print(ports_table)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging with rich handler."""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                show_time=True,
                show_path=False,
                markup=True,
            )
        ],
    )


def list_scans() -> None:
    """List all registered scans."""
    scans = ScanRegistry.all()

    if not scans:
        console.print("[yellow]No scans registered.[/yellow]")
        return

    table = Table(title="Available Scans", show_header=True)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Root Required", style="magenta")

    for scan_name, scan_class in sorted(scans.items()):
        scan_instance = scan_class()
        requires_root = "Yes" if scan_instance.requires_root else "No"
        table.add_row(
            scan_name,
            scan_instance.description or "No description",
            requires_root,
        )

    console.print(table)


async def run_workflow(
    target: str, output_dir: Path, workflow_name: str = "pentest"
) -> None:
    """Run the specified workflow."""
    # Currently only pentest workflow is implemented
    if workflow_name != "pentest":
        console.print(f"[red]Unknown workflow: {workflow_name}[/red]")
        sys.exit(1)

    console.print(f"\n[bold]Target:[/bold] {target}")
    console.print(f"[bold]Output Directory:[/bold] {output_dir}")
    console.print(f"[bold]Workflow:[/bold] {workflow_name}\n")

    # Create and run workflow
    workflow = PentestWorkflow(target, output_dir)

    try:
        ctx = await workflow.run()

        # Print results summary
        print_results_summary(ctx)

        # Save results
        console.print("\n[bold]Saving results...[/bold]")
        ResultStorage.save(ctx)
        ResultStorage.save_summary(ctx)

        console.print("\n[bold green]✓[/bold green] Workflow completed successfully!")
        console.print(f"Results saved to: [cyan]{output_dir}[/cyan]\n")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Workflow interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]✗ Workflow failed:[/bold red] {e}")
        logging.exception("Workflow error")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-Scout: Automated Reconnaissance Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run pentest workflow on target
  auto-scout 192.168.1.100

  # Specify output directory
  auto-scout 192.168.1.100 -o /tmp/scan_results

  # List all available scans
  auto-scout --list-scans

  # Enable verbose output
  auto-scout 192.168.1.100 -v
        """,
    )

    parser.add_argument(
        "target",
        nargs="?",
        help="Target IP address or hostname",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="./output",
        help="Output directory for results (default: ./output)",
    )

    parser.add_argument(
        "-w",
        "--workflow",
        default="pentest",
        help="Workflow to run (default: pentest)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--list-scans",
        action="store_true",
        help="List all available scans and exit",
    )

    parser.add_argument(
        "--discover",
        metavar="DIR",
        help="Discover and register scans from directory",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Print banner
    print_banner()

    # Discover user scans if specified
    if args.discover:
        console.print(f"[bold]Discovering scans in:[/bold] {args.discover}")
        ScanRegistry.discover(args.discover)
        console.print(f"[green]Discovered {len(ScanRegistry.all())} scans[/green]\n")

    # Auto-discover from default user_scans directory
    user_scans_dir = Path("./user_scans")
    if user_scans_dir.exists():
        ScanRegistry.discover(user_scans_dir)

    # List scans and exit
    if args.list_scans:
        list_scans()
        sys.exit(0)

    # Validate target
    if not args.target:
        console.print("[red]Error: target is required[/red]")
        parser.print_help()
        sys.exit(1)

    # Run workflow
    output_path = Path(args.output)
    asyncio.run(run_workflow(args.target, output_path, args.workflow))


if __name__ == "__main__":
    main()
