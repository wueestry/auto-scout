from port import Port
from utils.console_handler import ask_for_user_input
from utils.xml_parser import OutputParser


class Host:
    def __init__(self, ip: str | None = None) -> None:
        if not ip:
            ip = ask_for_user_input(msg="Enter the target IP:")

        self.ip: str = str(ip)

        self.open_ports: dict[str, Port] = {}

    def update_data(self, data: any, type: str) -> None:
        if type == "nmap":
            for detail in data:
                if detail.get('address') == self.ip:
                    for port_info in detail.get('ports', []):
                        port_number = str(port_info.get('port_id'))
                        if port_number in self.open_ports:
                            self.open_ports[port_number].update(info=port_info)
                        elif port_number:
                            port = Port(number=port_number)
                            port.update(info=port_info)
                            self.open_ports[port_number] = port
