import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.absolute()))


from auto_scout.host import Host
from auto_scout.scans.default_scans import run_quick_nmap, run_detailed_nmap, run_vuln_nmap
from auto_scout.utils.console_handler import print_welcome_msg


def main() -> None:
    print_welcome_msg()
    host = Host()
    run_quick_nmap(host=host)
    run_detailed_nmap(host=host)
    run_vuln_nmap(host=host)


if __name__ == "__main__":
    main()
