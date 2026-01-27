import subprocess
from rich.table import Table

from auto_scout.utils.console_handler import print_message, fill_simple_table
from auto_scout.utils.xml_parser import OutputParser


def run_cmd(cmd: str) -> str:
    result = subprocess.run(cmd.split(sep=" "), capture_output=True, text=True)
    return result.stdout


def process_cmd(cmd: str) -> any:
    print_message(msg=f"Running Command: {cmd}", colour="yellow")
    result = run_cmd(cmd=cmd)
    if "nmap" in cmd and "-oX" in cmd:
        parsed_result, result = process_nmap_cmd(cmd=cmd)
    else:
        parsed_result = None

    print_message(msg=result)

    return parsed_result
    

def process_nmap_cmd(cmd: str) -> tuple[any, Table]:
    cmd_parts = cmd.split(sep=" ")
    for c in cmd_parts:
        if c.endswith(".xml"):
            xml_file = c
            break
    with open(xml_file, "r") as file:
        xml_content = file.read()
    
    parsed_xml = OutputParser.parse_nmap_xml(xml_content)
    return parsed_xml, fill_simple_table(cmd=cmd, parsed_xml=parsed_xml)