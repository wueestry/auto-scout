"""Parser classes for different scan tools."""

from auto_scout.parsers.base import Parser
from auto_scout.parsers.nmap import NmapParser

__all__ = ["Parser", "NmapParser"]
