"""Built-in scans for auto-scout."""

# Scans will auto-register themselves when imported
from auto_scout.scans.nmap import QuickNmapScan, DetailedNmapScan, VulnNmapScan

__all__ = ["QuickNmapScan", "DetailedNmapScan", "VulnNmapScan"]
