"""Nmap-based scans."""

from auto_scout.scans.nmap.quick_scan import QuickNmapScan
from auto_scout.scans.nmap.detailed_scan import DetailedNmapScan
from auto_scout.scans.nmap.vuln_scan import VulnNmapScan

__all__ = ["QuickNmapScan", "DetailedNmapScan", "VulnNmapScan"]
