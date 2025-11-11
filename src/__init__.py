"""
IMFDB Game Data Scraper

A Python tool for scraping weapon data from IMFDB (Internet Movie Firearms Database).
"""

__version__ = "1.0.0"
__author__ = "MarlinZH"

from .scraper import IMFDBScraper
from .parser import WeaponParser
from .exporter import DataExporter

__all__ = ["IMFDBScraper", "WeaponParser", "DataExporter"]
