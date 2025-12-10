"""
Weapon deduplication functionality using multiple strategies
"""

import re
import hashlib
from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher
import logging


class WeaponDeduplicator:
    """Handles deduplication of weapon entries using multiple strategies"""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the deduplicator
        
        Args:
            verbose: Enable verbose logging (default: False)
        """
        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Thresholds for fuzzy matching
        self.name_similarity_threshold = 0.85
        self.partial_similarity_threshold = 0.90
        
        # Common weapon name variations to normalize
        self.normalize_patterns = [
            (r'\s+', ' '),  # Multiple spaces to single
            (r'[™®©]', ''),  # Remove trademark symbols
            (r'\s*\([^)]*\)\s*$', ''),  # Remove trailing parentheses
            (r'^\s+|\s+$', ''),  # Trim whitespace
        ]
    
    def deduplicate_weapons(self, weapons: List[Dict], 
                          strategy: str = 'comprehensive') -> Tuple[List[Dict], Dict]:
        """
        Deduplicate weapons using specified strategy
        
        Args:
            weapons: List of weapon dictionaries
            strategy: Deduplication strategy - 'exact', 'fuzzy', or 'comprehensive' (default)
            
        Returns:
            Tuple of (deduplicated weapons list, statistics dict)
        """
        self.logger.info(f"Starting deduplication of {len(weapons)} weapons using '{strategy}' strategy")
        
        if strategy == 'exact':
            result = self._deduplicate_exact(weapons)
        elif strategy == 'fuzzy':
            result = self._deduplicate_fuzzy(weapons)
        else:  # comprehensive
            result = self._deduplicate_comprehensive(weapons)
        
        unique_weapons, stats = result
        
        self.logger.info(f"Deduplication complete:")
        self.logger.info(f"  Original: {len(weapons)}")
        self.logger.info(f"  Unique: {len(unique_weapons)}")
        self.logger.info(f"  Duplicates removed: {stats['duplicates_removed']}")
        
        return unique_weapons, stats
    
    def _deduplicate_exact(self, weapons: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Deduplicate using exact name matching (fastest)
        
        Args:
            weapons: List of weapon dictionaries
            
        Returns:
            Tuple of (unique weapons, statistics)
        """
        seen_keys = set()
        unique_weapons = []
        duplicates = 0
        
        for weapon in weapons:
            # Create key from game + normalized weapon name
            key = self._create_exact_key(weapon)
            
            if key not in seen_keys:
                seen_keys.add(key)
                unique_weapons.append(weapon)
            else:
                duplicates += 1
                self.logger.debug(f"  Duplicate (exact): {weapon.get('toc_name', 'Unknown')}")
        
        stats = {
            'strategy': 'exact',
            'original_count': len(weapons),
            'unique_count': len(unique_weapons),
            'duplicates_removed': duplicates
        }
        
        return unique_weapons, stats
    
    def _deduplicate_fuzzy(self, weapons: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Deduplicate using fuzzy string matching (more accurate but slower)
        
        Args:
            weapons: List of weapon dictionaries
            
        Returns:
            Tuple of (unique weapons, statistics)
        """
        unique_weapons = []
        duplicates = 0
        
        for weapon in weapons:
            is_duplicate = False
            
            # Compare against all unique weapons so far
            for unique_weapon in unique_weapons:
                if self._are_weapons_similar(weapon, unique_weapon):
                    is_duplicate = True
                    duplicates += 1
                    self.logger.debug(
                        f"  Duplicate (fuzzy): {weapon.get('toc_name', 'Unknown')} "
                        f"≈ {unique_weapon.get('toc_name', 'Unknown')}"
                    )
                    break
            
            if not is_duplicate:
                unique_weapons.append(weapon)
        
        stats = {
            'strategy': 'fuzzy',
            'original_count': len(weapons),
            'unique_count': len(unique_weapons),
            'duplicates_removed': duplicates
        }
        
        return unique_weapons, stats
    
    def _deduplicate_comprehensive(self, weapons: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Comprehensive deduplication using multiple passes
        
        Args:
            weapons: List of weapon dictionaries
            
        Returns:
            Tuple of (unique weapons, statistics)
        """
        # Pass 1: Exact matching (fast)
        self.logger.debug("Pass 1: Exact matching")
        weapons_after_exact, stats_exact = self._deduplicate_exact(weapons)
        
        # Pass 2: Fuzzy matching on remaining weapons
        self.logger.debug("Pass 2: Fuzzy matching")
        weapons_after_fuzzy, stats_fuzzy = self._deduplicate_fuzzy(weapons_after_exact)
        
        # Pass 3: Hash-based detection for variations
        self.logger.debug("Pass 3: Hash-based detection")
        final_weapons, hash_duplicates = self._deduplicate_by_hash(weapons_after_fuzzy)
        
        total_duplicates = (
            stats_exact['duplicates_removed'] +
            stats_fuzzy['duplicates_removed'] +
            hash_duplicates
        )
        
        stats = {
            'strategy': 'comprehensive',
            'original_count': len(weapons),
            'unique_count': len(final_weapons),
            'duplicates_removed': total_duplicates,
            'pass_1_exact': stats_exact['duplicates_removed'],
            'pass_2_fuzzy': stats_fuzzy['duplicates_removed'],
            'pass_3_hash': hash_duplicates
        }
        
        return final_weapons, stats
    
    def _deduplicate_by_hash(self, weapons: List[Dict]) -> Tuple[List[Dict], int]:
        """
        Deduplicate using content hashing
        
        Args:
            weapons: List of weapon dictionaries
            
        Returns:
            Tuple of (unique weapons, number of duplicates removed)
        """
        seen_hashes = set()
        unique_weapons = []
        duplicates = 0
        
        for weapon in weapons:
            weapon_hash = self._compute_weapon_hash(weapon)
            
            if weapon_hash not in seen_hashes:
                seen_hashes.add(weapon_hash)
                unique_weapons.append(weapon)
            else:
                duplicates += 1
                self.logger.debug(f"  Duplicate (hash): {weapon.get('toc_name', 'Unknown')}")
        
        return unique_weapons, duplicates
    
    def _create_exact_key(self, weapon: Dict) -> str:
        """
        Create a normalized key for exact matching
        
        Args:
            weapon: Weapon dictionary
            
        Returns:
            Normalized key string
        """
        game = weapon.get('game', '').lower().strip()
        
        # Try multiple name fields in priority order
        name = (
            weapon.get('real_world_name', '') or
            weapon.get('toc_name', '') or
            weapon.get('in_game_name', '')
        )
        
        # Normalize the name
        normalized_name = self._normalize_name(name)
        
        return f"{game}|{normalized_name}"
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize weapon name for comparison
        
        Args:
            name: Weapon name to normalize
            
        Returns:
            Normalized name
        """
        name = name.lower()
        
        # Apply normalization patterns
        for pattern, replacement in self.normalize_patterns:
            name = re.sub(pattern, replacement, name)
        
        return name.strip()
    
    def _are_weapons_similar(self, weapon1: Dict, weapon2: Dict) -> bool:
        """
        Check if two weapons are similar using fuzzy matching
        
        Args:
            weapon1: First weapon dictionary
            weapon2: Second weapon dictionary
            
        Returns:
            True if weapons are similar, False otherwise
        """
        # Must be from the same game
        if weapon1.get('game', '').lower() != weapon2.get('game', '').lower():
            return False
        
        # Get all name variations for both weapons
        names1 = self._get_all_weapon_names(weapon1)
        names2 = self._get_all_weapon_names(weapon2)
        
        # Check if any combination of names is similar
        for name1 in names1:
            for name2 in names2:
                similarity = self._calculate_similarity(name1, name2)
                
                if similarity >= self.name_similarity_threshold:
                    return True
                
                # Also check if one is a substring of the other
                if self._is_partial_match(name1, name2):
                    return True
        
        return False
    
    def _get_all_weapon_names(self, weapon: Dict) -> List[str]:
        """
        Get all available name variations for a weapon
        
        Args:
            weapon: Weapon dictionary
            
        Returns:
            List of normalized name variations
        """
        names = []
        
        for field in ['real_world_name', 'toc_name', 'in_game_name']:
            name = weapon.get(field, '')
            if name:
                normalized = self._normalize_name(name)
                if normalized and normalized not in names:
                    names.append(normalized)
        
        return names
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _is_partial_match(self, str1: str, str2: str) -> bool:
        """
        Check if one string is a significant partial match of another
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            True if partial match detected
        """
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        # Check if either is contained in the other
        if str1_lower in str2_lower or str2_lower in str1_lower:
            # Calculate what percentage of the shorter string matches
            shorter = min(len(str1_lower), len(str2_lower))
            longer = max(len(str1_lower), len(str2_lower))
            
            # If the shorter string is at least 90% of the longer, consider it a match
            ratio = shorter / longer
            return ratio >= self.partial_similarity_threshold
        
        return False
    
    def _compute_weapon_hash(self, weapon: Dict) -> str:
        """
        Compute a hash for a weapon based on its content
        
        Args:
            weapon: Weapon dictionary
            
        Returns:
            Hash string
        """
        # Create a deterministic string representation
        hash_parts = [
            weapon.get('game', '').lower(),
            self._normalize_name(weapon.get('real_world_name', '')),
            self._normalize_name(weapon.get('in_game_name', '')),
            weapon.get('category', '').lower()
        ]
        
        # Remove empty parts
        hash_parts = [part for part in hash_parts if part]
        
        # Create hash
        hash_string = '|'.join(hash_parts)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def generate_deduplication_report(self, original_weapons: List[Dict],
                                     deduplicated_weapons: List[Dict],
                                     stats: Dict) -> str:
        """
        Generate a detailed deduplication report
        
        Args:
            original_weapons: Original weapons list
            deduplicated_weapons: Deduplicated weapons list
            stats: Statistics dictionary
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("DEDUPLICATION REPORT")
        report.append("=" * 60)
        report.append(f"\nStrategy: {stats['strategy']}")
        report.append(f"Original weapons: {stats['original_count']}")
        report.append(f"Unique weapons: {stats['unique_count']}")
        report.append(f"Duplicates removed: {stats['duplicates_removed']}")
        report.append(f"Reduction: {stats['duplicates_removed']/stats['original_count']*100:.1f}%")
        
        if 'pass_1_exact' in stats:
            report.append(f"\nPass breakdown:")
            report.append(f"  - Exact matching: {stats['pass_1_exact']} duplicates")
            report.append(f"  - Fuzzy matching: {stats['pass_2_fuzzy']} duplicates")
            report.append(f"  - Hash detection: {stats['pass_3_hash']} duplicates")
        
        # Group by game
        report.append(f"\nWeapons by game:")
        games = {}
        for weapon in deduplicated_weapons:
            game = weapon.get('game', 'Unknown')
            games[game] = games.get(game, 0) + 1
        
        for game, count in sorted(games.items()):
            report.append(f"  - {game}: {count} weapons")
        
        report.append("=" * 60)
        
        return "\n".join(report)
