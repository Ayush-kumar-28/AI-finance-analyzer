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

# Merchant name patterns (common formats)
MERCHANT_PATTERNS = [
    r'(?:to|from)\s+([a-z\s]+?)(?:\s+(?:upi|neft|imps|atm|pos))',
    r'([a-z]+(?:\s+[a-z]+){0,2})\s+(?:payment|purchase|order)',
]

# Stop words to remove (common but meaningless words)
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'must', 'can', 'ref', 'no', 'id',
    'txn', 'transaction', 'date', 'time', 'amount', 'balance', 'dr', 'cr',
}

# Category-specific keywords for better classification
CATEGORY_KEYWORDS = {
    'food': ['zomato', 'swiggy', 'restaurant', 'cafe', 'food', 'pizza', 'burger', 
             'dominos', 'mcdonalds', 'kfc', 'subway', 'starbucks', 'dunkin'],
    'transport': ['uber', 'ola', 'rapido', 'metro', 'bus', 'taxi', 'fuel', 
                  'petrol', 'diesel', 'parking', 'toll', 'fastag'],
    'shopping': ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'shopping',
                 'mall', 'store', 'retail', 'supermarket', 'grocery'],
    'utilities': ['electricity', 'water', 'gas', 'internet', 'broadband', 'mobile',
                  'recharge', 'bill', 'airtel', 'jio', 'vodafone', 'bsnl'],
    'entertainment': ['netflix', 'amazon prime', 'hotstar', 'spotify', 'youtube',
                      'movie', 'cinema', 'theatre', 'game', 'gaming'],
    'education': ['university', 'college', 'school', 'course', 'tuition', 'fees',
                  'education', 'learning', 'training', 'udemy', 'coursera'],
}


def clean_text(text: str) -> str:
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


def extract_merchant_name(text: str) -> str:
    """
    Extract merchant name from transaction description.
    
    Args:
        text: Raw transaction description
        
    Returns:
        Extracted merchant name or empty string
    """
    text = text.lower()
    
    for pattern in MERCHANT_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    # Fallback: take first 2-3 words
    words = clean_text(text).split()
    if words:
        return ' '.join(words[:min(3, len(words))])
    
    return ""


def get_category_hints(text: str) -> List[str]:
    """
    Get category hints based on keywords in text.
    
    Args:
        text: Cleaned transaction description
        
    Returns:
        List of potential categories
    """
    text = text.lower()
    hints = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                hints.append(category)
                break
    
    return hints


def enhance_features(text: str) -> Dict[str, any]:
    """
    Extract enhanced features from transaction text.
    
    Args:
        text: Raw transaction description
        
    Returns:
        Dictionary of extracted features
    """
    cleaned = clean_text(text)
    
    features = {
        'cleaned_text': cleaned,
        'merchant': extract_merchant_name(text),
        'category_hints': get_category_hints(cleaned),
        'word_count': len(cleaned.split()),
        'has_upi': 'upi' in text.lower(),
        'has_transfer': any(kw in text.lower() for kw in ['neft', 'imps', 'rtgs', 'transfer']),
        'has_atm': 'atm' in text.lower(),
    }
    
    return features


def batch_clean_text(texts: List[str]) -> List[str]:
    """
    Clean multiple texts efficiently.
    
    Args:
        texts: List of raw transaction descriptions
        
    Returns:
        List of cleaned texts
    """
    return [clean_text(text) for text in texts]


# Backward compatibility
def clean_transaction_text(text: str) -> str:
    """Alias for clean_text for backward compatibility."""
    return clean_text(text)
