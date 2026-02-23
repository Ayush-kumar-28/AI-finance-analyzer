"""
Advanced Data Cleaning Pipeline
Handles cleaning and preprocessing of bank statements (CSV, Excel, PDF)
with advanced anomaly detection, data validation, quality scoring, and adaptive learning

Enhanced with PostgreSQL storage using SQLAlchemy ORM
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
import pdfplumber
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import adaptive cleaner
from adaptive_cleaner import get_adaptive_cleaner


class DataCleaningPipeline:
    """
    Advanced data cleaning pipeline for bank statements.
    Handles CSV, Excel, and PDF formats with intelligent cleaning.
    
    Features:
    - Automatic format detection
    - Smart column mapping
    - Anomaly detection
    - Data quality scoring
    - Advanced validation
    - Outlier detection
    - Pattern recognition
    """
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.pdf']
        self.cleaning_stats = {
            'original_rows': 0,
            'cleaned_rows': 0,
            'removed_rows': 0,
            'format': None,
            'cleaning_steps': [],
            'anomalies_detected': [],
            'quality_score': 0.0,
            'warnings': []
        }
        
        # Advanced validation rules
        self.amount_min = 1
        self.amount_max = 10000000  # 1 crore
        self.description_min_length = 3
        self.description_max_length = 500
        
        # Pattern detection
        self.common_patterns = {
            'upi': r'\bupi\b',
            'neft': r'\bneft\b',
            'imps': r'\bimps\b',
            'atm': r'\batm\b',
            'card': r'\bcard\b',
        }
        
        # Initialize adaptive cleaner
        self.adaptive_cleaner = get_adaptive_cleaner()
        print("   🧠 Adaptive learning enabled")
    
    def clean_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Advanced cleaning pipeline - processes any supported file format.
        
        Args:
            file_path (str): Path to bank statement file
            
        Returns:
            DataFrame: Cleaned transactions with description and amount
            dict: Comprehensive cleaning statistics and quality metrics
        """
        print("\n" + "="*70)
        print("🧹 ADVANCED DATA CLEANING PIPELINE")
        print("="*70)
        
        # Reset stats
        self.cleaning_stats = {
            'original_rows': 0,
            'cleaned_rows': 0,
            'removed_rows': 0,
            'format': None,
            'cleaning_steps': [],
            'anomalies_detected': [],
            'quality_score': 0.0,
            'warnings': [],
            'patterns_found': {},
            'amount_stats': {},
            'processing_time': 0.0
        }
        
        start_time = datetime.now()
        
        # Step 1: Extract raw data
        file_ext = Path(file_path).suffix.lower()
        self.cleaning_stats['format'] = file_ext[1:].upper()
        
        print(f"\n📄 File: {Path(file_path).name}")
        print(f"📋 Format: {self.cleaning_stats['format']}")
        
        if file_ext == '.pdf':
            df = self._extract_pdf(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = self._extract_excel(file_path)
        elif file_ext == '.csv':
            df = self._extract_csv(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
        
        self.cleaning_stats['original_rows'] = len(df)
        print(f"✅ Extracted {len(df)} raw transactions")
        
        # Step 2: Advanced cleaning pipeline
        df = self._advanced_cleaning_pipeline(df)
        
        # Step 3: Detect anomalies
        self._detect_anomalies(df)
        
        # Step 4: Calculate quality score
        self._calculate_quality_score(df)
        
        # Step 5: Detect patterns
        self._detect_patterns(df)
        
        # Step 6: Calculate statistics
        self._calculate_statistics(df)
        
        self.cleaning_stats['cleaned_rows'] = len(df)
        self.cleaning_stats['removed_rows'] = (
            self.cleaning_stats['original_rows'] - 
            self.cleaning_stats['cleaned_rows']
        )
        
        # Calculate processing time
        end_time = datetime.now()
        self.cleaning_stats['processing_time'] = (end_time - start_time).total_seconds()
        
        # Step 7: Print comprehensive summary
        self._print_advanced_summary()
        
        return df, self.cleaning_stats
    
    def _extract_pdf(self, file_path):
        """Extract transactions from PDF with improved table detection."""
        print("\n🔍 Extracting from PDF...")
        
        transactions = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Try table extraction first
                    tables = page.extract_tables()
                    
                    if tables:
                        print(f"   Found {len(tables)} table(s) on page {page_num + 1}")
                        for table in tables:
                            transactions.extend(self._parse_pdf_table(table))
                    else:
                        # Fallback to text extraction
                        text = page.extract_text()
                        if text:
                            transactions.extend(self._parse_pdf_text(text))
        
        except Exception as e:
            print(f"   ⚠️  PDF extraction error: {e}")
            # Try text-based extraction as fallback
            with pdfplumber.open(file_path) as pdf:
                all_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
                transactions = self._parse_pdf_text('\n'.join(all_text))
        
        return pd.DataFrame(transactions)
    
    def _parse_pdf_table(self, table: List[List]) -> List[Dict]:
        """Parse PDF table into transactions."""
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
        
        # Find header row
        header_row = None
        for i, row in enumerate(table[:3]):  # Check first 3 rows
            if row and any(cell and ('description' in str(cell).lower() or 
                                    'date' in str(cell).lower() or
                                    'transaction' in str(cell).lower()) 
                          for cell in row):
                header_row = i
                break
        
        if header_row is None:
            header_row = 0
        
        headers = [str(cell).lower().strip() if cell else '' for cell in table[header_row]]
        
        # Find column indices
        desc_idx = None
        debit_idx = None
        credit_idx = None
        amount_idx = None
        
        for i, header in enumerate(headers):
            if any(kw in header for kw in ['description', 'transaction', 'particulars', 'narration', 'details']):
                desc_idx = i
            elif any(kw in header for kw in ['debit', 'withdrawal', 'paid', 'dr']):
                debit_idx = i
            elif any(kw in header for kw in ['credit', 'deposit', 'received', 'cr']):
                credit_idx = i
            elif 'amount' in header and amount_idx is None:
                amount_idx = i
        
        # Process data rows
        for row in table[header_row + 1:]:
            if not row or len(row) == 0:
                continue
            
            # Get description
            description = ''
            if desc_idx is not None and desc_idx < len(row):
                description = str(row[desc_idx]) if row[desc_idx] else ''
            
            if not description or description.lower() in ['none', 'null', '']:
                continue
            
            # Get amount and transaction type
            amount = 0
            transaction_type = None
            
            if amount_idx is not None and amount_idx < len(row):
                # Single amount column - detect type from description
                amount_str = str(row[amount_idx]) if row[amount_idx] else '0'
                amount = self._parse_amount(amount_str)
                # Will detect transaction_type later from description
            elif debit_idx is not None or credit_idx is not None:
                debit = 0
                credit = 0
                
                if debit_idx is not None and debit_idx < len(row):
                    debit_str = str(row[debit_idx]) if row[debit_idx] else '0'
                    debit = self._parse_amount(debit_str)
                
                if credit_idx is not None and credit_idx < len(row):
                    credit_str = str(row[credit_idx]) if row[credit_idx] else '0'
                    credit = self._parse_amount(credit_str)
                
                # Determine transaction type based on which column has value
                if credit > 0 and debit == 0:
                    amount = credit
                    transaction_type = 'credit'
                elif debit > 0 and credit == 0:
                    amount = debit
                    transaction_type = 'debit'
                elif credit > 0 and debit > 0:
                    # Both have values - use the larger one
                    if credit > debit:
                        amount = credit
                        transaction_type = 'credit'
                    else:
                        amount = debit
                        transaction_type = 'debit'
            
            if amount > 0 and len(description) > 3:
                transaction = {
                    'description': description,
                    'amount': amount
                }
                if transaction_type:
                    transaction['transaction_type'] = transaction_type
                transactions.append(transaction)
        
        return transactions
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        try:
            # Remove currency symbols and commas
            amount_str = str(amount_str).replace('₹', '').replace(',', '').strip()

            # Remove any leading non-numeric characters (like "T 850.00" -> "850.00")
            # Keep only digits and decimal point
            cleaned = ''
            for char in amount_str:
                if char.isdigit() or char == '.':
                    cleaned += char

            if not cleaned or cleaned.lower() in ['none', 'null', '']:
                return 0.0
            return float(cleaned)
        except:
            return 0.0


    
    def _parse_pdf_text(self, text):
        """Parse PDF text to extract transactions."""
        transactions = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or any(header in line for header in [
                'Transaction Statement', 'Date Transaction', 'Balance',
                'Opening Balance', 'Closing Balance'
            ]):
                continue
            
            # Look for date pattern
            date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
            
            if re.search(date_pattern, line):
                # Extract amount with currency symbol
                amount_pattern = r'₹\s*([0-9,]+\.?\d*)'
                amounts = re.findall(amount_pattern, line)
                
                if amounts:
                    # Get description (text before amount)
                    desc_match = re.split(amount_pattern, line)[0]
                    description = re.sub(date_pattern, '', desc_match).strip()
                    
                    # Clean description
                    description = re.sub(r'\s+', ' ', description)
                    
                    # Get amount (last one is usually the transaction amount)
                    amount_str = amounts[-1].replace(',', '')
                    try:
                        amount = float(amount_str)
                        
                        # Validate amount range
                        if 1 <= amount <= 10000000:  # ₹1 to ₹1 crore
                            if description and len(description) > 3:
                                transactions.append({
                                    'description': description,
                                    'amount': amount
                                })
                    except ValueError:
                        continue
        
        return transactions
    
    def _extract_excel(self, file_path):
        """Extract transactions from Excel."""
        print("\n📊 Extracting from Excel...")
        df = pd.read_excel(file_path)
        file_name = Path(file_path).name
        return self._standardize_columns(df, file_name)
    
    def _extract_csv(self, file_path):
        """Extract transactions from CSV."""
        print("\n📄 Extracting from CSV...")
        df = pd.read_csv(file_path)
        file_name = Path(file_path).name
        return self._standardize_columns(df, file_name)
    
    def _standardize_columns(self, df, file_name: str = None):
        """Standardize column names and structure with adaptive learning."""
        try:
            # Check if transaction_type already exists (from PDF extraction)
            has_transaction_type = 'transaction_type' in df.columns
            
            # Convert all column names to lowercase
            df.columns = df.columns.str.lower().str.strip()
            
            original_columns = list(df.columns)
            print(f"   Available columns: {original_columns}")
            
            # If transaction_type already exists from PDF, just ensure we have description and amount
            if has_transaction_type:
                print(f"   ✅ transaction_type already detected from PDF")
                if 'description' in df.columns and 'amount' in df.columns:
                    return df[['description', 'amount', 'transaction_type']]
            
            # Detect bank format
            bank_format = self.adaptive_cleaner.detect_bank_format(original_columns)
            
            # Get suggested column mapping
            suggested_mapping = self.adaptive_cleaner.suggest_column_mapping(original_columns)
            print(f"   💡 Suggested mapping: {suggested_mapping}")
            
            # Find description column using adaptive learning
            desc_col = suggested_mapping.get('description')
            if not desc_col:
                # Fallback to manual search
                desc_cols = ['description', 'narration', 'transaction details', 
                             'particulars', 'details', 'remarks', 'transaction', 'desc']
                for col in desc_cols:
                    if col in df.columns:
                        desc_col = col
                        # Learn this variation
                        self.adaptive_cleaner.add_column_variation('description', col)
                        break
            
            if not desc_col:
                raise ValueError(f"Could not find description column. Available columns: {original_columns}")
            
            print(f"   Using description column: {desc_col}")
            
            # Find amount column(s) using adaptive learning
            amount_col = suggested_mapping.get('amount')
            debit_col = suggested_mapping.get('debit')
            credit_col = suggested_mapping.get('credit')
            
            # Override with exact matches if they exist (more reliable than adaptive learning)
            if 'debit' in df.columns:
                debit_col = 'debit'
            if 'credit' in df.columns:
                credit_col = 'credit'
            if 'amount' in df.columns:
                amount_col = 'amount'
            
            if amount_col and amount_col in df.columns:
                # Single amount column - assume all are expenses unless description indicates credit
                result_df = df[[desc_col, amount_col]].copy()
                result_df.columns = ['description', 'amount']
                
                # Ensure description is string type
                result_df['description'] = result_df['description'].astype(str)
                
                # Detect transaction type from description
                result_df['transaction_type'] = 'debit'  # default
                credit_keywords = ['credit', 'credited', 'deposit', 'received', 'salary', 'income', 'refund', 'cashback', 'interest']
                for keyword in credit_keywords:
                    mask = result_df['description'].str.contains(keyword, case=False, na=False)
                    result_df.loc[mask, 'transaction_type'] = 'credit'
                
                print(f"   Using single amount column: {amount_col}")
                print(f"   Detected {(result_df['transaction_type'] == 'credit').sum()} credit transactions")
            elif debit_col or credit_col:
                # Debit/credit columns
                if not debit_col:
                    # Search for debit column
                    debit_cols = ['debit', 'withdrawal', 'dr', 'paid', 'withdraw']
                    for col in debit_cols:
                        if col in df.columns:
                            debit_col = col
                            self.adaptive_cleaner.add_column_variation('debit', col)
                            break
                
                if not credit_col:
                    # Search for credit column
                    credit_cols = ['credit', 'deposit', 'cr', 'received', 'deposited']
                    for col in credit_cols:
                        if col in df.columns:
                            credit_col = col
                            self.adaptive_cleaner.add_column_variation('credit', col)
                            break
                
                print(f"   Found debit column: {debit_col}")
                print(f"   Found credit column: {credit_col}")
                
                if debit_col and credit_col:
                    # Both columns - keep track of transaction type
                    df[debit_col] = pd.to_numeric(df[debit_col], errors='coerce')
                    df[credit_col] = pd.to_numeric(df[credit_col], errors='coerce')
                    df[debit_col] = df[debit_col].replace(0, np.nan)
                    df[credit_col] = df[credit_col].replace(0, np.nan)
                    
                    # Create amount column
                    df['amount'] = df[debit_col].fillna(0) + df[credit_col].fillna(0)
                    
                    # Add transaction_type column (credit or debit)
                    df['transaction_type'] = 'debit'  # default
                    df.loc[df[credit_col].notna(), 'transaction_type'] = 'credit'
                    
                    result_df = df[[desc_col, 'amount', 'transaction_type']].copy()
                    result_df.columns = ['description', 'amount', 'transaction_type']
                    
                    # Ensure description is string type
                    result_df['description'] = result_df['description'].astype(str)
                elif debit_col:
                    # Only debit
                    df[debit_col] = pd.to_numeric(df[debit_col], errors='coerce')
                    df['transaction_type'] = 'debit'
                    result_df = df[[desc_col, debit_col, 'transaction_type']].copy()
                    result_df.columns = ['description', 'amount', 'transaction_type']
                elif credit_col:
                    # Only credit
                    df[credit_col] = pd.to_numeric(df[credit_col], errors='coerce')
                    df['transaction_type'] = 'credit'
                    result_df = df[[desc_col, credit_col, 'transaction_type']].copy()
                    result_df.columns = ['description', 'amount', 'transaction_type']
                else:
                    raise ValueError(f"Could not find amount columns. Available columns: {original_columns}")
            else:
                raise ValueError(f"Could not find amount columns. Available columns: {original_columns}")
            
            # Learn this format for future use
            self.adaptive_cleaner.learn_format(original_columns, file_name)
            
            # Ensure we have the right columns
            if 'description' not in result_df.columns or 'amount' not in result_df.columns:
                raise ValueError(f"Failed to create standard columns. Got: {list(result_df.columns)}")
            
            return result_df
            
        except Exception as e:
            print(f"   ❌ Column standardization error: {e}")
            raise ValueError(f"Column standardization failed: {e}")
    
    def _clean_pipeline(self, df):
        """Apply cleaning steps to the dataframe."""
        print("\n🧹 Applying cleaning steps...")
        
        # Step 1: Remove null values
        original_len = len(df)
        df = df.dropna(subset=['description', 'amount'])
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} rows with null values")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} null rows")
        
        # Step 2: Remove duplicate transactions
        original_len = len(df)
        df = df.drop_duplicates(subset=['description', 'amount'])
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} duplicate transactions")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} duplicates")
        
        # Step 3: Clean descriptions
        df['description'] = df['description'].apply(self._clean_description)
        print(f"   ✅ Cleaned transaction descriptions")
        self.cleaning_stats['cleaning_steps'].append("Cleaned descriptions")
        
        # Step 4: Validate amounts
        original_len = len(df)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df[df['amount'] > 0]  # Remove zero or negative amounts
        df = df[df['amount'] <= 10000000]  # Remove unrealistic amounts (> 1 crore)
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} rows with invalid amounts")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} invalid amounts")
        
        # Step 5: Remove very short descriptions
        original_len = len(df)
        df = df[df['description'].str.len() >= 3]
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} rows with too short descriptions")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} short descriptions")
        
        # Step 6: Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _advanced_cleaning_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced cleaning pipeline with intelligent validation."""
        print("\n🧹 Applying advanced cleaning steps...")
        
        # Step 1: Remove null values
        original_len = len(df)
        df = df.dropna(subset=['description', 'amount'])
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} rows with null values")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} null rows")
        
        # Step 2: Remove exact duplicates (conservative approach)
        original_len = len(df)
        # Check for description+amount duplicates
        dup_mask = df.duplicated(subset=['description', 'amount'], keep=False)
        
        if dup_mask.any():
            # Count how many times each description+amount pair appears
            dup_counts = df[dup_mask].groupby(['description', 'amount']).size()
            
            # Only remove if there are MORE than 2 identical transactions
            # (2 identical transactions might be legitimate, e.g., bi-weekly salary)
            suspicious_dups = dup_counts[dup_counts > 2]
            
            if len(suspicious_dups) > 0:
                # Remove only the suspicious ones (keep first 2, remove rest)
                for (desc, amt), count in suspicious_dups.items():
                    mask = (df['description'] == desc) & (df['amount'] == amt)
                    # Keep first 2, remove rest
                    indices = df[mask].index[2:]
                    df = df.drop(indices)
                    removed = len(indices)
                    print(f"   ✅ Removed {removed} suspicious duplicates: {desc[:40]}")
                    self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} suspicious duplicates")
            else:
                # All duplicates appear only 2 times - keep them (might be legitimate)
                print(f"   ℹ️  Found {len(dup_counts)} pairs of duplicate transactions (kept - might be legitimate)")
                self.cleaning_stats['warnings'].append(
                    f"Found {len(dup_counts)} pairs of duplicate transactions (kept for review)"
                )
        
        # Step 3: Detect and handle near-duplicates (fuzzy matching)
        original_len = len(df)
        df = self._remove_near_duplicates(df)
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} near-duplicate transactions")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} near-duplicates")
        
        # Step 4: Advanced description cleaning
        df['description'] = df['description'].apply(self._advanced_clean_description)
        print(f"   ✅ Applied advanced description cleaning")
        self.cleaning_stats['cleaning_steps'].append("Advanced description cleaning")
        
        # Step 5: Validate and normalize amounts
        original_len = len(df)
        df = self._validate_amounts(df)
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} rows with invalid amounts")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} invalid amounts")
        
        # Step 6: Remove outliers using IQR method
        original_len = len(df)
        df = self._remove_outliers(df)
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} statistical outliers")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} outliers")
        
        # Step 7: Validate description quality
        original_len = len(df)
        df = self._validate_descriptions(df)
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} rows with poor quality descriptions")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} poor descriptions")
        
        # Step 8: Remove test/dummy transactions
        original_len = len(df)
        df = self._remove_test_transactions(df)
        if len(df) < original_len:
            removed = original_len - len(df)
            print(f"   ✅ Removed {removed} test/dummy transactions")
            self.cleaning_stats['cleaning_steps'].append(f"Removed {removed} test transactions")
        
        # Step 9: Standardize formatting
        df = self._standardize_formatting(df)
        print(f"   ✅ Standardized formatting")
        self.cleaning_stats['cleaning_steps'].append("Standardized formatting")
        
        # Step 10: Ensure transaction_type exists for all rows
        if 'transaction_type' not in df.columns:
            df['transaction_type'] = 'debit'  # default
        
        # Fill missing transaction_type by detecting from description
        missing_type_mask = df['transaction_type'].isna()
        if missing_type_mask.any():
            credit_keywords = ['credit', 'credited', 'deposit', 'received', 'salary', 'income', 'refund', 'cashback', 'interest']
            for keyword in credit_keywords:
                mask = missing_type_mask & df['description'].str.contains(keyword, case=False, na=False)
                df.loc[mask, 'transaction_type'] = 'credit'
            
            # Fill remaining as debit
            df['transaction_type'] = df['transaction_type'].fillna('debit')
            
            detected_credits = (df['transaction_type'] == 'credit').sum()
            print(f"   ✅ Detected transaction types: {detected_credits} credits, {len(df) - detected_credits} debits")
            self.cleaning_stats['cleaning_steps'].append(f"Detected transaction types")
        
        # Step 11: Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _remove_near_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove near-duplicate transactions using similarity threshold."""
        if len(df) < 2:
            return df
        
        to_remove = set()
        
        for i in range(len(df)):
            if i in to_remove:
                continue
            
            for j in range(i + 1, len(df)):
                if j in to_remove:
                    continue
                
                # Check if descriptions are similar and amounts are close
                desc1 = df.iloc[i]['description'].lower()
                desc2 = df.iloc[j]['description'].lower()
                amt1 = df.iloc[i]['amount']
                amt2 = df.iloc[j]['amount']
                
                # DON'T remove exact duplicates here - they were already handled in Step 2
                # Only remove near-duplicates (similar but not identical)
                if desc1 == desc2 and abs(amt1 - amt2) < 0.01:
                    # Skip exact duplicates - already handled
                    continue
                elif self._similarity_score(desc1, desc2) > 0.9 and abs(amt1 - amt2) < 1:
                    # Only remove if similarity is high but not exact
                    to_remove.add(j)
        
        return df.drop(list(to_remove)).reset_index(drop=True)
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate simple similarity score between two strings."""
        if not s1 or not s2:
            return 0.0
        
        # Jaccard similarity on words
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _advanced_clean_description(self, text: str) -> str:
        """Advanced description cleaning with pattern recognition."""
        if not isinstance(text, str):
            return str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\./]', ' ', text)
        
        # Remove long transaction IDs (10+ digits)
        text = re.sub(r'\b\d{10,}\b', '', text)
        
        # Remove dates in various formats
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)
        text = re.sub(r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', '', text)
        
        # Remove times
        text = re.sub(r'\b\d{1,2}:\d{2}(?::\d{2})?\b', '', text)
        
        # Remove reference numbers
        text = re.sub(r'\b(?:ref|txn|id|no|num)[\s:]*[a-z0-9]+\b', '', text, flags=re.IGNORECASE)
        
        # Remove account numbers (4-16 digits)
        text = re.sub(r'\b\d{4,16}\b', '', text)
        
        # Remove currency symbols
        text = re.sub(r'[₹$€£¥]', '', text)
        
        # Remove multiple slashes
        text = re.sub(r'/+', ' ', text)
        
        # Remove multiple dots
        text = re.sub(r'\.{2,}', '', text)
        
        # Remove extra whitespace again
        text = re.sub(r'\s+', ' ', text)
        
        # Strip and return
        return text.strip()
    
    def _validate_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and normalize amount values."""
        # Convert to numeric
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Remove NaN amounts
        df = df.dropna(subset=['amount'])
        
        # Remove zero or negative amounts
        df = df[df['amount'] > self.amount_min]
        
        # Remove unrealistic amounts
        df = df[df['amount'] <= self.amount_max]
        
        # Round to 2 decimal places
        df['amount'] = df['amount'].round(2)
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove statistical outliers using IQR method (only for expenses, not income)."""
        if len(df) < 10:  # Skip if too few transactions
            return df
        
        # Don't remove outliers - they could be legitimate large transactions
        # like salary, rent, etc. Just flag them as warnings
        Q1 = df['amount'].quantile(0.25)
        Q3 = df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier bounds (more lenient: 3 * IQR)
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        # Identify outliers but DON'T remove them
        outliers_mask = (df['amount'] < lower_bound) | (df['amount'] > upper_bound)
        outliers = df[outliers_mask]
        
        if len(outliers) > 0:
            # Just log as warning, don't remove
            self.cleaning_stats['warnings'].append(
                f"Detected {len(outliers)} potential outliers (amounts outside 3*IQR): " +
                f"₹{outliers['amount'].min():.0f} - ₹{outliers['amount'].max():.0f}"
            )
            print(f"   ⚠️  Found {len(outliers)} potential outliers (kept in data)")
        
        # Return all data - don't remove outliers
        return df
    
    def _validate_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate description quality."""
        # Remove too short descriptions
        df = df[df['description'].str.len() >= self.description_min_length]
        
        # Remove too long descriptions (likely corrupted)
        df = df[df['description'].str.len() <= self.description_max_length]
        
        # Remove descriptions with only numbers
        df = df[~df['description'].str.match(r'^\d+$')]
        
        # Remove descriptions with only special characters
        df = df[df['description'].str.match(r'.*[a-zA-Z].*')]
        
        return df
    
    def _remove_test_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove test, dummy, or invalid transactions."""
        test_patterns = [
            r'\btest\b',
            r'\bdummy\b',
            r'\bsample\b',
            r'\bexample\b',
            r'\bxxx\b',
            r'\b000\b',
            r'\b999\b',
        ]
        
        pattern = '|'.join(test_patterns)
        mask = ~df['description'].str.contains(pattern, case=False, regex=True, na=False)
        
        return df[mask]
    
    def _standardize_formatting(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize text formatting."""
        # Trim whitespace
        df['description'] = df['description'].str.strip()
        
        # Ensure consistent spacing
        df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True)
        
        return df
    
    def _detect_anomalies(self, df: pd.DataFrame):
        """Detect anomalies in the cleaned data."""
        anomalies = []
        
        # Check for suspiciously round amounts
        round_amounts = df[df['amount'] % 1000 == 0]
        if len(round_amounts) > len(df) * 0.5:
            anomalies.append(f"High proportion of round amounts ({len(round_amounts)}/{len(df)})")
        
        # Check for repeated amounts
        amount_counts = df['amount'].value_counts()
        repeated = amount_counts[amount_counts > 5]
        if len(repeated) > 0:
            anomalies.append(f"Found {len(repeated)} amounts repeated >5 times")
        
        # Check for very similar descriptions
        desc_counts = df['description'].value_counts()
        repeated_desc = desc_counts[desc_counts > 10]
        if len(repeated_desc) > 0:
            anomalies.append(f"Found {len(repeated_desc)} descriptions repeated >10 times")
        
        self.cleaning_stats['anomalies_detected'] = anomalies
    
    def _calculate_quality_score(self, df: pd.DataFrame):
        """Calculate data quality score (0-100)."""
        score = 100.0
        
        # Deduct for data loss
        if self.cleaning_stats['original_rows'] > 0:
            retention_rate = len(df) / self.cleaning_stats['original_rows']
            if retention_rate < 0.9:
                score -= (0.9 - retention_rate) * 100
        
        # Deduct for anomalies
        score -= len(self.cleaning_stats['anomalies_detected']) * 5
        
        # Deduct for warnings
        score -= len(self.cleaning_stats['warnings']) * 3
        
        # Bonus for good description quality
        avg_desc_length = df['description'].str.len().mean()
        if avg_desc_length > 20:
            score += 5
        
        # Ensure score is between 0-100
        self.cleaning_stats['quality_score'] = max(0, min(100, score))
    
    def _detect_patterns(self, df: pd.DataFrame):
        """Detect common transaction patterns."""
        patterns_found = {}
        
        for pattern_name, pattern_regex in self.common_patterns.items():
            count = df['description'].str.contains(
                pattern_regex, case=False, regex=True, na=False
            ).sum()
            if count > 0:
                patterns_found[pattern_name] = int(count)
        
        self.cleaning_stats['patterns_found'] = patterns_found
    
    def _calculate_statistics(self, df: pd.DataFrame):
        """Calculate amount statistics."""
        if len(df) > 0:
            self.cleaning_stats['amount_stats'] = {
                'min': float(df['amount'].min()),
                'max': float(df['amount'].max()),
                'mean': float(df['amount'].mean()),
                'median': float(df['amount'].median()),
                'std': float(df['amount'].std()) if len(df) > 1 else 0.0,
                'total': float(df['amount'].sum())
            }
    
    def _clean_description(self, text):
        """Clean transaction description text."""
        if not isinstance(text, str):
            return str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Remove transaction IDs (long numbers)
        text = re.sub(r'\b\d{10,}\b', '', text)
        
        # Remove dates
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)
        
        # Remove extra whitespace again
        text = re.sub(r'\s+', ' ', text)
        
        # Strip and title case
        text = text.strip()
        
        return text
    
    def _print_advanced_summary(self):
        """Print comprehensive cleaning summary with quality metrics."""
        print("\n" + "="*70)
        print("📊 ADVANCED CLEANING SUMMARY")
        print("="*70)
        
        # Basic stats
        print(f"\n📋 Basic Statistics:")
        print(f"   • Format: {self.cleaning_stats['format']}")
        print(f"   • Original rows: {self.cleaning_stats['original_rows']}")
        print(f"   • Cleaned rows: {self.cleaning_stats['cleaned_rows']}")
        print(f"   • Removed rows: {self.cleaning_stats['removed_rows']}")
        
        retention_rate = 0
        if self.cleaning_stats['original_rows'] > 0:
            retention_rate = (self.cleaning_stats['cleaned_rows'] / 
                            self.cleaning_stats['original_rows'] * 100)
        print(f"   • Retention rate: {retention_rate:.1f}%")
        print(f"   • Processing time: {self.cleaning_stats['processing_time']:.2f}s")
        
        # Quality score
        quality = self.cleaning_stats['quality_score']
        quality_emoji = "🟢" if quality >= 80 else "🟡" if quality >= 60 else "🔴"
        print(f"\n{quality_emoji} Data Quality Score: {quality:.1f}/100")
        
        # Cleaning steps
        if self.cleaning_stats['cleaning_steps']:
            print(f"\n🧹 Cleaning Steps Applied ({len(self.cleaning_stats['cleaning_steps'])}):")
            for step in self.cleaning_stats['cleaning_steps']:
                print(f"   • {step}")
        
        # Patterns detected
        if self.cleaning_stats['patterns_found']:
            print(f"\n🔍 Transaction Patterns Detected:")
            for pattern, count in self.cleaning_stats['patterns_found'].items():
                print(f"   • {pattern.upper()}: {count} transactions")
        
        # Amount statistics
        if self.cleaning_stats['amount_stats']:
            stats = self.cleaning_stats['amount_stats']
            print(f"\n💰 Amount Statistics:")
            print(f"   • Min: ₹{stats['min']:.2f}")
            print(f"   • Max: ₹{stats['max']:.2f}")
            print(f"   • Mean: ₹{stats['mean']:.2f}")
            print(f"   • Median: ₹{stats['median']:.2f}")
            print(f"   • Std Dev: ₹{stats['std']:.2f}")
            print(f"   • Total: ₹{stats['total']:.2f}")
        
        # Anomalies
        if self.cleaning_stats['anomalies_detected']:
            print(f"\n⚠️  Anomalies Detected ({len(self.cleaning_stats['anomalies_detected'])}):")
            for anomaly in self.cleaning_stats['anomalies_detected']:
                print(f"   • {anomaly}")
        
        # Warnings
        if self.cleaning_stats['warnings']:
            print(f"\n⚡ Warnings ({len(self.cleaning_stats['warnings'])}):")
            for warning in self.cleaning_stats['warnings']:
                print(f"   • {warning}")
        
        print("="*70 + "\n")
    
    def _print_summary(self):
        """Print basic cleaning summary (legacy method)."""
        print("\n" + "="*60)
        print("📊 CLEANING SUMMARY")
        print("="*60)
        print(f"Format: {self.cleaning_stats['format']}")
        print(f"Original rows: {self.cleaning_stats['original_rows']}")
        print(f"Cleaned rows: {self.cleaning_stats['cleaned_rows']}")
        print(f"Removed rows: {self.cleaning_stats['removed_rows']}")
        print(f"Retention rate: {(self.cleaning_stats['cleaned_rows'] / self.cleaning_stats['original_rows'] * 100):.1f}%")
        
        if self.cleaning_stats['cleaning_steps']:
            print("\nCleaning steps applied:")
            for step in self.cleaning_stats['cleaning_steps']:
                print(f"   • {step}")
        
        print("="*60 + "\n")


# Convenience function
def clean_bank_statement(file_path):
    """
    Clean a bank statement file.
    
    Args:
        file_path (str): Path to file
        
    Returns:
        DataFrame: Cleaned transactions
        dict: Cleaning statistics
    """
    pipeline = DataCleaningPipeline()
    return pipeline.clean_file(file_path)


if __name__ == "__main__":
    # Test the pipeline
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        df, stats = clean_bank_statement(file_path)
        print(f"\n✅ Cleaned {len(df)} transactions")
        print("\nFirst 5 transactions:")
        print(df.head())
    else:
        print("Usage: python data_cleaning_pipeline.py <file_path>")
