from auto_scout.utils.nist import NISThtml
import survey
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_welcome_msg() -> None:
    console.print(
        Panel.fit(
            renderable="""
▄▖  ▗     ▄▖      ▗ 
▌▌▌▌▜▘▛▌▄▖▚ ▛▘▛▌▌▌▜▘
▛▌▙▌▐▖▙▌  ▄▌▙▖▙▌▙▌▐▖
            """,
            subtitle="[dim]by wueestry[/dim]",
            border_style="bright_blue",
        )
    )


def print_message(msg: str, colour: str = "default") -> None:
    if colour == "default":
        console.print(msg)
    else:
        console.print(f"[{colour}]{msg}[/{colour}]")


def ask_for_user_input(msg: str) -> str | None:
    result = survey.routines.input(msg)
    if result:
        return str(result)
    else:
        print_message(msg="No input given. Try again", colour="red")
        return ask_for_user_input(msg=msg)


def create_scan_table(cmd: str) -> Table:
    nmap_table = Table(title=f"NMAP run info: {cmd}")
    nmap_table.add_column("Protocol", justify="right", style="cyan", no_wrap=True)
    nmap_table.add_column("Port ID", justify="right", style="magenta", no_wrap=True)
    nmap_table.add_column("Service", justify="right", style="green")
    nmap_table.add_column("CPE", justify="right", style="blue")
    nmap_table.add_column("Advisories", justify="right", style="blue")
    return nmap_table


def fill_simple_table(cmd: str, parsed_xml: dict[str, any]) -> Table:
    nmap_table = create_scan_table(cmd=cmd)
    cpe_details = NISThtml().correlate_nmap_with_nids(parsed_xml=parsed_xml)
    for row_data in parsed_xml:
        ports = row_data['ports']
        for port_data in ports:
            advisories = []
            for cpe in port_data['cpes']:
                if cpe in cpe_details:  # Service may not have an advisory
                    for nist in cpe_details[cpe]:
                        advisories.append(
                            f"[bold][yellow]link={nist.link}[/yellow][/bold], "
                            f"{nist.summary}, [red]score={nist.score}[/red]"
                        )
            nmap_table.add_row(
                port_data['protocol'],
                port_data['port_id'],
                f"{port_data['service_name']} {port_data['service_product']} {port_data['service_version']}",
                "\n".join(port_data['cpes']),
                "\n".join(advisories)
            )
    return nmap_table
