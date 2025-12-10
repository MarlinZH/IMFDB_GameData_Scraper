"""
IMFDB Game Data Scraper

A comprehensive tool for scraping weapon data and images from IMFDB.
"""

from .scraper import IMFDBScraper
from .parser import WeaponParser
from .exporter import DataExporter
from .deduplicator import WeaponDeduplicator
from .image_scraper import WeaponImageScraper

__all__ = [
    'IMFDBScraper',
    'WeaponParser',
    'DataExporter',
    'WeaponDeduplicator',
    'WeaponImageScraper'
]

__version__ = '1.1.0'
