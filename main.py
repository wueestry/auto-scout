import re
import subprocess

import survey
from rich.console import Console
from rich.panel import Panel


def main() -> None:
    console = Console()

    console.print(
        Panel.fit(
            """
▄▖  ▗     ▄▖      ▗ 
▌▌▌▌▜▘▛▌▄▖▚ ▛▘▛▌▌▌▜▘
▛▌▙▌▐▖▙▌  ▄▌▙▖▙▌▙▌▐▖
            """,
            subtitle="[dim]by wueestry[/dim]",
            border_style="bright_blue",
        )
    )

    ip_address = str(survey.routines.input("Enter the target IP address: "))
    ports = nmap_default_scan(console, ip_address)
    nmap_specific_scan(console, ip_address, ports)


def nmap_default_scan(console: Console, ip: str) -> list[str]:
    console.print(f"[bold yellow]Running Nmap Default Scan on {ip}...[/bold yellow]")
    console.print(
        f"[bold green]sudo nmap -sS -Pn -p- --max-retries 3 --min-rate 1000 -oN nmap_quick.txt {ip}[/bold green]"
    )
    result = subprocess.run(
        [
            "sudo",
            "nmap",
            "-sS",
            "-Pn",
            "-p-",
            "--max-retries",
            "5",
            "--min-rate",
            "1000",
            "-oN",
            "nmap_quick.txt",
            "-oX",
            "nmap_quick.xml",
            ip,
        ],
        capture_output=True,
        text=True,
    )
    console.print("[yellow]Nmap scan completed.[/yellow]")
    console.print(result.stdout)

    if result.stdout and "PORT" in result.stdout:
        block = result.stdout.split("PORT", 1)[1]
        ports: list[str] = re.findall(r"\b\d+(?=/(?:tcp|udp)\b)", block)
    else:
        ports = []

    return ports


def nmap_specific_scan(console: Console, ip: str, ports: list[str]) -> None:
    port_list = ",".join(ports)

    console.print(
        f"[bold yellow]Running Detailed Nmap Scan on Found Ports {port_list}[/bold yellow]"
    )
    console.print(
        f"[bold green]sudo nmap -sV -sC -O -p {port_list} -oN nmap_detailed.txt {ip}[/bold green]"
    )
    result = subprocess.run(
        [
            "sudo",
            "nmap",
            "-sV",
            "-sC",
            "-O",
            "-p",
            port_list,
            "-oN",
            "nmap_detailed.txt",
            "-oX",
            "nmap_detailed.xml",
            ip,
        ]
    )
    console.print("[yellow]Nmap scan completed.[/yellow]")
    console.print(result.stdout)

def nmap_vulnerabilities_scan(console: Console, ip: str, ports: list[str]) -> None:
    pass


if __name__ == "__main__":
    main()

