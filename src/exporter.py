"""
Data export functionality for weapons data
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
import logging


class DataExporter:
    """Handles exporting weapon data to various formats"""
    
    def __init__(self, output_dir: str = "output", verbose: bool = False):
        """
        Initialize the exporter
        
        Args:
            output_dir: Directory to save output files (default: "output")
            verbose: Enable verbose logging (default: False)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
    
    def save_csv(self, weapons: List[Dict], filename: str = "weapons.csv"):
        """
        Save weapons data to CSV
        
        Args:
            weapons: List of weapon dictionaries
            filename: Output filename (default: "weapons.csv")
        """
        if not weapons:
            self.logger.warning("No weapons data to save")
            return
        
        filepath = self.output_dir / filename
        df = pd.DataFrame(weapons)
        df.to_csv(filepath, index=False)
        self.logger.info(f"✓ Saved CSV to {filepath}")
    
    def save_json(self, weapons: List[Dict], filename: str = "weapons.json"):
        """
        Save weapons data to JSON
        
        Args:
            weapons: List of weapon dictionaries
            filename: Output filename (default: "weapons.json")
        """
        if not weapons:
            self.logger.warning("No weapons data to save")
            return
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(weapons, f, indent=2, ensure_ascii=False)
        self.logger.info(f"✓ Saved JSON to {filepath}")
    
    def save_markdown(self, weapons: List[Dict], filename: str = "weapons.md"):
        """
        Save weapons data to Markdown table
        
        Args:
            weapons: List of weapon dictionaries
            filename: Output filename (default: "weapons.md")
        """
        if not weapons:
            self.logger.warning("No weapons data to save")
            return
        
        filepath = self.output_dir / filename
        df = pd.DataFrame(weapons)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# IMFDB Weapons Data\n\n")
            f.write(f"Total weapons: {len(weapons)}\n\n")
            f.write(df.to_markdown(index=False))
        
        self.logger.info(f"✓ Saved Markdown to {filepath}")
    
    def save_all(self, weapons: List[Dict], base_filename: str = "weapons"):
        """
        Save weapons data in all formats
        
        Args:
            weapons: List of weapon dictionaries
            base_filename: Base filename without extension (default: "weapons")
        """
        self.save_csv(weapons, f"{base_filename}.csv")
        self.save_json(weapons, f"{base_filename}.json")
        self.save_markdown(weapons, f"{base_filename}.md")
    
    def print_summary(self, weapons: List[Dict]):
        """
        Print summary statistics about the weapons data
        
        Args:
            weapons: List of weapon dictionaries
        """
        if not weapons:
            self.logger.warning("No weapons data to summarize")
            return
        
        df = pd.DataFrame(weapons)
        
        print("\n" + "="*60)
        print("WEAPONS DATA SUMMARY")
        print("="*60)
        print(f"\nTotal weapons found: {len(weapons)}")
        print(f"Games: {df['game'].nunique()}")
        print(f"Categories: {df['category'].nunique()}")
        
        print("\n--- Weapons per game ---")
        print(df['game'].value_counts().to_string())
        
        print("\n--- Weapons per category ---")
        category_counts = df['category'].value_counts()
        print(category_counts.head(10).to_string())
        if len(category_counts) > 10:
            print(f"... and {len(category_counts) - 10} more categories")
        
        # Calculate extraction success rates
        real_world_success = (df['real_world_name'] != '').sum()
        ingame_different = (df['toc_name'] != df['in_game_name']).sum()
        
        print("\n--- Extraction statistics ---")
        print(f"Real-world names found: {real_world_success}/{len(weapons)} "
              f"({real_world_success/len(weapons)*100:.1f}%)")
        print(f"In-game names differ from TOC: {ingame_different}/{len(weapons)} "
              f"({ingame_different/len(weapons)*100:.1f}%)")
        
        # Show sample data
        print("\n--- Sample data (first 5 weapons) ---")
        print(df.head(5).to_string(index=False))
        
        # Show weapons with both names found
        both_names = df[(df['real_world_name'] != '') & (df['in_game_name'] != df['toc_name'])]
        if not both_names.empty:
            print("\n--- Weapons with both real-world and in-game names (first 5) ---")
            print(both_names[['game', 'toc_name', 'real_world_name', 'in_game_name']].head(5).to_string(index=False))
        
        print("\n" + "="*60 + "\n")
