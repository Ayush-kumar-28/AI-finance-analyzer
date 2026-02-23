"""
Enhanced NLP Text Cleaner for Transaction Descriptions
Includes advanced preprocessing techniques for better accuracy
"""

import re
from typing import List, Dict

# Common bank transaction keywords and their normalized forms
BANK_KEYWORDS = {
    'upi': 'upi',
    'neft': 'transfer',
    'imps': 'transfer',
    'rtgs': 'transfer',
    'atm': 'atm',
    'pos': 'pos',
    'emi': 'emi',
    'ecs': 'ecs',
    'nach': 'nach',
}

# Stop words to remove (common but meaningless words)
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'must', 'can', 'ref', 'no', 'id',
    'txn', 'transaction', 'date', 'time', 'amount', 'balance', 'dr', 'cr',
}


def clean_text(text):
    """
    Enhanced text cleaning with advanced NLP techniques.
    
    Args:
        text: Raw transaction description
        
    Returns:
        Cleaned and normalized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove dates (various formats)
    text = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', '', text)
    text = re.sub(r'\d{2,4}[-/]\d{1,2}[-/]\d{1,2}', '', text)
    
    # Remove times
    text = re.sub(r'\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]m)?', '', text)
    
    # Remove transaction IDs and reference numbers
    text = re.sub(r'(?:ref|txn|id|no|num)[\s:]*[a-z0-9]+', '', text)
    
    # Remove account numbers
    text = re.sub(r'\b\d{4,}\b', '', text)
    
    # Remove currency symbols and amounts
    text = re.sub(r'[₹$€£¥]\s*\d+(?:,\d+)*(?:\.\d+)?', '', text)
    text = re.sub(r'\b\d+(?:,\d+)*(?:\.\d+)?\s*(?:rs|inr|usd|eur)\b', '', text)
    
    # Normalize bank keywords
    for keyword, normalized in BANK_KEYWORDS.items():
        text = re.sub(r'\b' + keyword + r'\b', normalized, text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove stop words
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    
    # Join back
    text = ' '.join(words)
    
    return text.strip()
