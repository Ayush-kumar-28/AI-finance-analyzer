"""
Adaptive Data Cleaning System
Learns from uploaded files to handle different bank statement formats automatically
"""

import json
import os
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd


class AdaptiveDataCleaner:
    """
    Learns column mappings and patterns from uploaded files
    to automatically handle different bank statement formats.
    """
    
    def __init__(self, config_file: str = 'ml-service/cleaning_patterns.json'):
        self.config_file = config_file
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict:
        """Load learned patterns from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default patterns
        return {
            'column_mappings': {
                'description': [
                    'description', 'narration', 'transaction details',
                    'particulars', 'details', 'remarks', 'transaction',
                    'desc', 'txn details', 'transaction description'
                ],
                'amount': ['amount', 'value', 'transaction amount'],
                'debit': [
                    'debit', 'withdrawal', 'dr', 'paid', 'withdraw',
                    'debit amount', 'withdrawals', 'payment'
                ],
                'credit': [
                    'credit', 'deposit', 'cr', 'received', 'deposited',
                    'credit amount', 'deposits', 'receipt'
                ],
                'date': [
                    'date', 'transaction date', 'txn date', 'value date',
                    'posting date', 'trans date'
                ],
                'balance': [
                    'balance', 'closing balance', 'available balance',
                    'running balance', 'bal'
                ]
            },
            'bank_formats': {},
            'learned_patterns': [],
            'statistics': {
                'files_processed': 0,
                'formats_learned': 0,
                'last_updated': None
            }
        }
    
    def _save_patterns(self):
        """Save learned patterns to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save patterns: {e}")
    
    def detect_bank_format(self, columns: List[str]) -> str:
        """
        Detect which bank format this file matches.
        
        Args:
            columns: List of column names from the file
            
        Returns:
            Bank format identifier or 'unknown'
        """
        columns_lower = [col.lower().strip() for col in columns]
        columns_set = set(columns_lower)
        
        # Check against known bank formats
        for bank_name, format_info in self.patterns['bank_formats'].items():
            known_columns = set(format_info['columns'])
            
            # If 80% of columns match, consider it the same format
            match_ratio = len(columns_set & known_columns) / len(known_columns)
            if match_ratio >= 0.8:
                print(f"   🏦 Detected format: {bank_name} ({match_ratio*100:.0f}% match)")
                return bank_name
        
        return 'unknown'
    
    def learn_format(self, columns: List[str], file_name: str = None):
        """
        Learn a new bank statement format.
        
        Args:
            columns: List of column names from the file
            file_name: Optional file name for reference
        """
        columns_lower = [col.lower().strip() for col in columns]
        
        # Try to identify bank from filename
        bank_name = 'unknown'
        if file_name:
            file_lower = file_name.lower()
            common_banks = ['hdfc', 'icici', 'sbi', 'axis', 'kotak', 'pnb', 'bob']
            for bank in common_banks:
                if bank in file_lower:
                    bank_name = bank.upper()
                    break
        
        # If still unknown, generate a format ID
        if bank_name == 'unknown':
            format_count = len(self.patterns['bank_formats'])
            bank_name = f'Format_{format_count + 1}'
        
        # Store the format
        if bank_name not in self.patterns['bank_formats']:
            self.patterns['bank_formats'][bank_name] = {
                'columns': columns_lower,
                'first_seen': datetime.now().isoformat(),
                'times_seen': 1,
                'file_examples': [file_name] if file_name else []
            }
            self.patterns['statistics']['formats_learned'] += 1
            print(f"   📚 Learned new format: {bank_name}")
        else:
            # Update existing format
            self.patterns['bank_formats'][bank_name]['times_seen'] += 1
            if file_name and file_name not in self.patterns['bank_formats'][bank_name]['file_examples']:
                self.patterns['bank_formats'][bank_name]['file_examples'].append(file_name)
        
        self.patterns['statistics']['files_processed'] += 1
        self.patterns['statistics']['last_updated'] = datetime.now().isoformat()
        self._save_patterns()
    
    def suggest_column_mapping(self, columns: List[str]) -> Dict[str, str]:
        """
        Suggest column mappings based on learned patterns.
        
        Args:
            columns: List of column names from the file
            
        Returns:
            Dictionary mapping standard names to actual column names
        """
        columns_lower = [col.lower().strip() for col in columns]
        mapping = {}
        
        # Try to map each standard column type
        for standard_name, variations in self.patterns['column_mappings'].items():
            for col in columns_lower:
                if col in variations:
                    mapping[standard_name] = col
                    break
                # Fuzzy matching
                for variation in variations:
                    if variation in col or col in variation:
                        mapping[standard_name] = col
                        break
                if standard_name in mapping:
                    break
        
        return mapping
    
    def add_column_variation(self, standard_name: str, new_variation: str):
        """
        Add a new column name variation to the learned patterns.
        
        Args:
            standard_name: Standard column name (description, amount, etc.)
            new_variation: New variation to add
        """
        new_variation = new_variation.lower().strip()
        
        if standard_name in self.patterns['column_mappings']:
            if new_variation not in self.patterns['column_mappings'][standard_name]:
                self.patterns['column_mappings'][standard_name].append(new_variation)
                print(f"   📝 Learned new variation: '{new_variation}' → {standard_name}")
                self._save_patterns()
    
    def get_statistics(self) -> Dict:
        """Get statistics about learned patterns."""
        return {
            'files_processed': self.patterns['statistics']['files_processed'],
            'formats_learned': len(self.patterns['bank_formats']),
            'column_variations': {
                name: len(variations) 
                for name, variations in self.patterns['column_mappings'].items()
            },
            'known_banks': list(self.patterns['bank_formats'].keys()),
            'last_updated': self.patterns['statistics']['last_updated']
        }
    
    def get_format_info(self, bank_name: str) -> Dict:
        """Get information about a specific bank format."""
        return self.patterns['bank_formats'].get(bank_name, {})
    
    def export_patterns(self, output_file: str):
        """Export learned patterns to a file."""
        with open(output_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
        print(f"✅ Patterns exported to {output_file}")
    
    def import_patterns(self, input_file: str):
        """Import patterns from a file."""
        with open(input_file, 'r') as f:
            imported = json.load(f)
        
        # Merge with existing patterns
        for standard_name, variations in imported.get('column_mappings', {}).items():
            if standard_name in self.patterns['column_mappings']:
                for var in variations:
                    if var not in self.patterns['column_mappings'][standard_name]:
                        self.patterns['column_mappings'][standard_name].append(var)
            else:
                self.patterns['column_mappings'][standard_name] = variations
        
        # Merge bank formats
        for bank_name, format_info in imported.get('bank_formats', {}).items():
            if bank_name not in self.patterns['bank_formats']:
                self.patterns['bank_formats'][bank_name] = format_info
        
        self._save_patterns()
        print(f"✅ Patterns imported from {input_file}")


# Global instance
_adaptive_cleaner = None

def get_adaptive_cleaner() -> AdaptiveDataCleaner:
    """Get or create adaptive cleaner singleton."""
    global _adaptive_cleaner
    if _adaptive_cleaner is None:
        _adaptive_cleaner = AdaptiveDataCleaner()
    return _adaptive_cleaner


if __name__ == "__main__":
    # Test the adaptive cleaner
    cleaner = AdaptiveDataCleaner()
    
    print("Adaptive Data Cleaner Statistics:")
    print(json.dumps(cleaner.get_statistics(), indent=2))
    
    # Test column mapping
    test_columns = ['Transaction Details', 'Debit Amount', 'Credit Amount', 'Balance']
    mapping = cleaner.suggest_column_mapping(test_columns)
    print(f"\nSuggested mapping for {test_columns}:")
    print(json.dumps(mapping, indent=2))
