"""Nmap XML output parser."""

import logging
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from auto_scout.parsers.base import Parser

logger = logging.getLogger(__name__)


class NmapParser(Parser):
    """Parser for Nmap XML output."""

    def parse(self, source: str | Path) -> dict[str, Any]:
        """
        Parse Nmap output from file or string.

        Args:
            source: Either path to XML file or XML string

        Returns:
            Parsed data dictionary
        """
        if isinstance(source, Path) or (
            isinstance(source, str) and Path(source).exists()
        ):
            return self.parse_file(Path(source))
        else:
            return self.parse_string(str(source))

    def parse_file(self, file_path: Path) -> dict[str, Any]:
        """
        Parse Nmap XML output from a file.

        Args:
            file_path: Path to the XML file

        Returns:
            Parsed data dictionary with hosts and ports
        """
        try:
            with open(file_path) as f:
                xml_content = f.read()
            return self.parse_string(xml_content)
        except FileNotFoundError:
            logger.error(f"Nmap XML file not found: {file_path}")
            return {"hosts": [], "error": "File not found"}
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {"hosts": [], "error": str(e)}

    def parse_string(self, content: str) -> dict[str, Any]:
        """
        Parse Nmap XML output from a string.

        Args:
            content: XML content as string

        Returns:
            Parsed data dictionary with structure:
            {
                "args": "nmap command arguments",
                "hosts": [
                    {
                        "address": "192.168.1.1",
                        "ports": [
                            {
                                "port_id": "80",
                                "protocol": "tcp",
                                "state": "open",
                                "service_name": "http",
                                "service_product": "Apache",
                                "service_version": "2.4.41",
                                "cpes": ["cpe:/a:apache:http_server:2.4.41"]
                            }
                        ]
                    }
                ],
                "ports": [...]  # Flattened list of all ports
            }
        """
        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as e:
            logger.error(f"Failed to parse XML: {e}")
            return {"hosts": [], "ports": [], "error": f"XML parse error: {e}"}

        # Get nmap arguments
        nmap_args = root.attrib.get("args", "")

        hosts: list[dict[str, Any]] = []
        all_ports: list[dict[str, Any]] = []

        for host in root.findall("host"):
            # Get host address
            address_elem = host.find("address")
            if address_elem is None:
                continue

            host_address = address_elem.attrib.get("addr", "")
            if not host_address:
                continue

            host_data: dict[str, Any] = {"address": host_address, "ports": []}

            # Find all ports
            ports_elem = host.find("ports")
            if ports_elem is not None:
                for port_elem in ports_elem.findall("port"):
                    port_info = self._parse_port(port_elem)
                    if port_info:
                        host_data["ports"].append(port_info)
                        all_ports.append(port_info)

            hosts.append(host_data)

        return {
            "args": nmap_args,
            "hosts": hosts,
            "ports": all_ports,  # Flattened list for convenience
        }

    def _parse_port(self, port_elem: ElementTree.Element) -> dict[str, Any] | None:
        """
        Parse a single port element.

        Args:
            port_elem: XML element representing a port

        Returns:
            Dictionary with port information or None if port is closed
        """
        port_id = port_elem.attrib.get("portid", "")
        protocol = port_elem.attrib.get("protocol", "tcp")

        # Get port state
        state_elem = port_elem.find("state")
        if state_elem is None:
            return None

        state = state_elem.attrib.get("state", "")

        # Skip closed ports
        if state == "closed":
            return None

        port_info: dict[str, Any] = {
            "port_id": port_id,
            "protocol": protocol,
            "state": state,
            "service_name": "",
            "service_product": "",
            "service_version": "",
            "service_extrainfo": "",
            "cpes": [],
        }

        # Parse service information
        service_elem = port_elem.find("service")
        if service_elem is not None:
            port_info["service_name"] = service_elem.attrib.get("name", "")
            port_info["service_product"] = service_elem.attrib.get("product", "")
            port_info["service_version"] = service_elem.attrib.get("version", "")
            port_info["service_extrainfo"] = service_elem.attrib.get("extrainfo", "")

            # Parse CPE entries
            cpes = []
            for cpe_elem in service_elem.findall("cpe"):
                if cpe_elem.text:
                    cpes.append(cpe_elem.text)
            port_info["cpes"] = cpes

        # Parse script output (for vuln scans, etc.)
        scripts = {}
        for script_elem in port_elem.findall("script"):
            script_id = script_elem.attrib.get("id", "")
            script_output = script_elem.attrib.get("output", "")
            if script_id:
                scripts[script_id] = script_output

        if scripts:
            port_info["scripts"] = scripts

        return port_info
