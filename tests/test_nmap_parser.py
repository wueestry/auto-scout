"""Tests for Nmap parser."""

import tempfile
from pathlib import Path

import pytest

from auto_scout.parsers.nmap import NmapParser


@pytest.fixture
def nmap_parser() -> NmapParser:
    """Create NmapParser instance."""
    return NmapParser()


@pytest.fixture
def simple_nmap_xml() -> str:
    """Simple nmap XML output with one host and one open port."""
    return """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap -p 80 192.168.1.1">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="Apache httpd" version="2.4.41">
          <cpe>cpe:/a:apache:http_server:2.4.41</cpe>
        </service>
      </port>
    </ports>
  </host>
</nmaprun>"""


@pytest.fixture
def complex_nmap_xml() -> str:
    """Complex nmap XML output with multiple hosts and ports."""
    return """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap -sV -p- 192.168.1.0/24">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="7.9">
          <cpe>cpe:/a:openbsd:openssh:7.9</cpe>
        </service>
      </port>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="nginx" version="1.18.0"/>
      </port>
      <port protocol="tcp" portid="443">
        <state state="open" reason="syn-ack"/>
        <service name="https" product="nginx" version="1.18.0" tunnel="ssl">
          <cpe>cpe:/a:nginx:nginx:1.18.0</cpe>
        </service>
      </port>
    </ports>
  </host>
  <host>
    <address addr="192.168.1.2" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="3306">
        <state state="open" reason="syn-ack"/>
        <service name="mysql" product="MySQL" version="5.7.32"/>
      </port>
    </ports>
  </host>
</nmaprun>"""


@pytest.fixture
def nmap_with_scripts_xml() -> str:
    """Nmap XML with script output."""
    return """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap --script vuln 192.168.1.1">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="Apache httpd" version="2.4.41"/>
        <script id="http-vuln-cve2017-5638" output="VULNERABLE">
          <elem key="state">VULNERABLE</elem>
          <elem key="description">Apache Struts2 vulnerability</elem>
        </script>
        <script id="http-csrf" output="No CSRF protection found"/>
      </port>
    </ports>
  </host>
</nmaprun>"""


def test_parse_simple_xml(nmap_parser: NmapParser, simple_nmap_xml: str) -> None:
    """Test parsing simple nmap XML output."""
    result = nmap_parser.parse_string(simple_nmap_xml)

    assert "hosts" in result
    assert "ports" in result
    assert "args" in result

    # Check arguments
    assert result["args"] == "nmap -p 80 192.168.1.1"

    # Check hosts
    assert len(result["hosts"]) == 1
    host = result["hosts"][0]
    assert host["address"] == "192.168.1.1"
    assert len(host["ports"]) == 1

    # Check port details
    port = host["ports"][0]
    assert port["port_id"] == "80"
    assert port["protocol"] == "tcp"
    assert port["state"] == "open"
    assert port["service_name"] == "http"
    assert port["service_product"] == "Apache httpd"
    assert port["service_version"] == "2.4.41"
    assert "cpe:/a:apache:http_server:2.4.41" in port["cpes"]

    # Check flattened ports list
    assert len(result["ports"]) == 1
    assert result["ports"][0] == port


def test_parse_complex_xml(nmap_parser: NmapParser, complex_nmap_xml: str) -> None:
    """Test parsing complex nmap XML with multiple hosts and ports."""
    result = nmap_parser.parse_string(complex_nmap_xml)

    # Check hosts
    assert len(result["hosts"]) == 2

    # Check first host
    host1 = result["hosts"][0]
    assert host1["address"] == "192.168.1.1"
    assert len(host1["ports"]) == 3

    # Check SSH port
    ssh_port = host1["ports"][0]
    assert ssh_port["port_id"] == "22"
    assert ssh_port["service_name"] == "ssh"
    assert ssh_port["service_product"] == "OpenSSH"
    assert ssh_port["service_version"] == "7.9"

    # Check HTTP port
    http_port = host1["ports"][1]
    assert http_port["port_id"] == "80"
    assert http_port["service_name"] == "http"
    assert http_port["service_product"] == "nginx"

    # Check HTTPS port
    https_port = host1["ports"][2]
    assert https_port["port_id"] == "443"
    assert https_port["service_name"] == "https"
    assert "cpe:/a:nginx:nginx:1.18.0" in https_port["cpes"]

    # Check second host
    host2 = result["hosts"][1]
    assert host2["address"] == "192.168.1.2"
    assert len(host2["ports"]) == 1

    mysql_port = host2["ports"][0]
    assert mysql_port["port_id"] == "3306"
    assert mysql_port["service_name"] == "mysql"

    # Check flattened ports list (should have all 4 ports)
    assert len(result["ports"]) == 4


def test_parse_with_scripts(
    nmap_parser: NmapParser, nmap_with_scripts_xml: str
) -> None:
    """Test parsing nmap XML with script output."""
    result = nmap_parser.parse_string(nmap_with_scripts_xml)

    assert len(result["hosts"]) == 1
    host = result["hosts"][0]
    port = host["ports"][0]

    # Check scripts (stored as dict with script_id: output)
    assert "scripts" in port
    assert len(port["scripts"]) == 2

    # Check vulnerability script
    assert "http-vuln-cve2017-5638" in port["scripts"]
    assert "VULNERABLE" in port["scripts"]["http-vuln-cve2017-5638"]

    # Check CSRF script
    assert "http-csrf" in port["scripts"]
    assert "No CSRF protection found" in port["scripts"]["http-csrf"]


def test_parse_file(nmap_parser: NmapParser, simple_nmap_xml: str) -> None:
    """Test parsing nmap XML from file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(simple_nmap_xml)
        temp_path = Path(f.name)

    try:
        result = nmap_parser.parse_file(temp_path)

        assert "hosts" in result
        assert len(result["hosts"]) == 1
        assert result["hosts"][0]["address"] == "192.168.1.1"
    finally:
        temp_path.unlink()


def test_parse_nonexistent_file(nmap_parser: NmapParser) -> None:
    """Test parsing a file that doesn't exist."""
    result = nmap_parser.parse_file(Path("/nonexistent/file.xml"))

    assert "error" in result
    assert "File not found" in result["error"]
    assert result["hosts"] == []


def test_parse_invalid_xml(nmap_parser: NmapParser) -> None:
    """Test parsing invalid XML."""
    invalid_xml = "<invalid>This is not valid XML"

    result = nmap_parser.parse_string(invalid_xml)

    assert "error" in result
    assert "XML parse error" in result["error"]


def test_parse_empty_xml(nmap_parser: NmapParser) -> None:
    """Test parsing empty/minimal XML."""
    empty_xml = """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap 192.168.1.1">
</nmaprun>"""

    result = nmap_parser.parse_string(empty_xml)

    assert "hosts" in result
    assert len(result["hosts"]) == 0
    assert len(result["ports"]) == 0


def test_parse_closed_ports(nmap_parser: NmapParser) -> None:
    """Test parsing nmap output with closed ports (closed ports are skipped)."""
    closed_port_xml = """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap -p 80,443 192.168.1.1">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http"/>
      </port>
      <port protocol="tcp" portid="443">
        <state state="closed" reason="reset"/>
      </port>
    </ports>
  </host>
</nmaprun>"""

    result = nmap_parser.parse_string(closed_port_xml)

    host = result["hosts"][0]
    # Closed ports are skipped by the parser, so only open port should be present
    assert len(host["ports"]) == 1

    # Only the open port (80) should be parsed
    port_80 = host["ports"][0]
    assert port_80["state"] == "open"
    assert port_80["port_id"] == "80"


def test_parse_port_without_service(nmap_parser: NmapParser) -> None:
    """Test parsing port without service information."""
    no_service_xml = """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap -p 9999 192.168.1.1">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="9999">
        <state state="open" reason="syn-ack"/>
      </port>
    </ports>
  </host>
</nmaprun>"""

    result = nmap_parser.parse_string(no_service_xml)

    port = result["hosts"][0]["ports"][0]
    assert port["port_id"] == "9999"
    assert port["state"] == "open"
    # Service fields should be empty strings
    assert port["service_name"] == ""
    assert port["service_product"] == ""
    assert port["service_version"] == ""


def test_parse_multiple_cpes(nmap_parser: NmapParser) -> None:
    """Test parsing port with multiple CPEs."""
    multi_cpe_xml = """<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap 192.168.1.1">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="Apache httpd" version="2.4.41">
          <cpe>cpe:/a:apache:http_server:2.4.41</cpe>
          <cpe>cpe:/o:linux:linux_kernel</cpe>
          <cpe>cpe:/a:php:php:7.4</cpe>
        </service>
      </port>
    </ports>
  </host>
</nmaprun>"""

    result = nmap_parser.parse_string(multi_cpe_xml)

    port = result["hosts"][0]["ports"][0]
    assert len(port["cpes"]) == 3
    assert "cpe:/a:apache:http_server:2.4.41" in port["cpes"]
    assert "cpe:/o:linux:linux_kernel" in port["cpes"]
    assert "cpe:/a:php:php:7.4" in port["cpes"]
