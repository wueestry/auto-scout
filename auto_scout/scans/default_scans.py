from auto_scout.host import Host
from auto_scout.utils.cmd_handler import process_cmd

def run_quick_nmap(host: Host) -> None:
    cmd = f"sudo nmap -sS -Pn -p- --max-retries 3 --min-rate 1000 -oN nmap_quick.txt -oX nmap_quick.xml {host.ip}"
    parsed_result = process_cmd(cmd=cmd)
    host.update_data(data=parsed_result, type="nmap")

def run_detailed_nmap(host: Host) -> None:
    ports = ",".join(host.open_ports.keys())
    cmd = f"sudo nmap -sV -sC -A -O -p {ports} -oN nmap_detailed.txt -oX nmap_detailed.xml {host.ip}"
    parsed_result = process_cmd(cmd=cmd)
    host.update_data(data=parsed_result, type="nmap")

def run_vuln_nmap(host: Host) -> None:
    ports = ",".join(host.open_ports.keys())
    cmd = f"sudo nmap -p {ports} -oN nmap_vuln.txt -oX nmap_vuln.xml {host.ip} --script vuln"
    parsed_result = process_cmd(cmd=cmd)
    host.update_data(data=parsed_result, type="nmap")
