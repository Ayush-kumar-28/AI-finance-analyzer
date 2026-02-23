"""
Enhanced Transaction Classifier with Advanced ML Techniques
Includes confidence scoring, fallback rules, and performance optimization
"""

import pickle
import os
import sys
import numpy as np
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.text_cleaner import clean_text, get_category_hints, enhance_features

class TransactionClassifier:
    """
    Enhanced classifier service for transaction categorization.
    Uses TF-IDF + Linear SVM with confidence scoring and rule-based fallbacks.
    """
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_models()
        
        # Rule-based patterns for high-confidence classification
        self.rule_patterns = {
            'Food': ['zomato', 'swiggy', 'restaurant', 'cafe', 'dominos', 'mcdonalds', 'kfc', 'food', 'grocery', 'groceries', 'supermarket', 'big bazaar', 'dmart', 'reliance fresh', 'more supermarket', 'bigbasket', 'grofers', 'blinkit', 'zepto', 'dunzo', 'instamart', 'vegetables', 'fruits', 'dairy', 'milk', 'bread'],
            'Transport': ['uber', 'ola', 'rapido', 'metro', 'fuel', 'petrol', 'diesel', 'fastag'],
            'Shopping': ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'shopping'],
            'Bills': ['electricity bill', 'water bill', 'gas bill', 'mobile recharge', 'broadband bill', 'internet bill', 'dth recharge', 'landline bill', 'telephone bill', 'maintenance charges', 'property tax', 'bill payment', 'electricity board', 'water supply', 'gas cylinder', 'prepaid recharge', 'postpaid bill', 'airtel', 'jio', 'vodafone', 'bsnl', 'rent payment', 'house rent', 'monthly rent', 'apartment rent', 'flat rent', 'landlord', 'lease payment', 'rental', 'accommodation rent', 'housing rent'],
            'Investment': ['mutual fund', 'sip', 'systematic investment', 'stock purchase', 'share purchase', 'equity', 'demat', 'trading', 'zerodha', 'upstox', 'groww', 'angel broking', 'gold investment', 'fixed deposit', 'recurring deposit', 'ppf', 'epf', 'nps', 'pension fund', 'bond', 'cryptocurrency', 'crypto', 'bitcoin', 'ethereum', 'ulip', 'investment plan'],
            'Utilities': ['electricity', 'water', 'gas', 'internet', 'broadband', 'mobile', 'recharge'],
            'Entertainment': ['netflix', 'prime', 'hotstar', 'spotify', 'youtube', 'movie', 'cinema'],
            'Education': ['university', 'college', 'school', 'fees', 'tuition', 'course'],
            'ATM': ['atm', 'cash withdrawal'],
            'Transfer': ['neft', 'imps', 'rtgs', 'transfer', 'sent to', 'paid to'],
            'Medical': ['hospital', 'pharmacy', 'doctor', 'clinic', 'medical', 'medicine', 'apollo', 'fortis', 'max hospital', 'health', 'dental', 'lab test', 'checkup', '1mg', 'pharmeasy', 'netmeds', 'practo', 'physio', 'therapy'],
            'Income': ['salary', 'credited', 'income', 'bonus', 'refund'],
            'Cashback': ['cashback', 'reward', 'points'],
        }
    
    def load_models(self):
        """Load trained models from disk with error handling."""
        model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        
        model_path = os.path.join(model_dir, 'svm_model.pkl')
        vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
            raise FileNotFoundError(
                "Models not found. Please run training/train_model.py first."
            )
        
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            print("✅ ML models loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load models: {e}")
    
    def apply_rules(self, text: str) -> Tuple[str, float]:
        """
        Apply rule-based classification for high-confidence cases.
        Priority: Income > Cashback > Medical > Bills > Investment > Other categories
        
        Args:
            text: Cleaned transaction description
            
        Returns:
            Tuple of (category, confidence) or (None, 0.0) if no match
        """
        text_lower = text.lower()
        
        # Priority 1: Check for Income keywords FIRST (highest priority)
        income_patterns = self.rule_patterns.get('Income', [])
        for pattern in income_patterns:
            if pattern in text_lower:
                return 'Income', 0.95
        
        # Priority 2: Check for Cashback
        cashback_patterns = self.rule_patterns.get('Cashback', [])
        for pattern in cashback_patterns:
            if pattern in text_lower:
                return 'Cashback', 0.95
        
        # Priority 3: Check for Medical (before Shopping to avoid pharmacy being classified as shopping)
        medical_patterns = self.rule_patterns.get('Medical', [])
        for pattern in medical_patterns:
            if pattern in text_lower:
                return 'Medical', 0.95
        
        # Priority 4: Check for Bills (before Utilities to catch specific bill payments)
        bills_patterns = self.rule_patterns.get('Bills', [])
        for pattern in bills_patterns:
            if pattern in text_lower:
                return 'Bills', 0.95
        
        # Priority 5: Check for Investment (before Transfer to catch mutual fund transfers)
        investment_patterns = self.rule_patterns.get('Investment', [])
        for pattern in investment_patterns:
            if pattern in text_lower:
                return 'Investment', 0.95
        
        # Priority 6: Check other categories
        for category, patterns in self.rule_patterns.items():
            if category in ['Income', 'Cashback', 'Medical', 'Bills', 'Investment']:  # Already checked
                continue
            for pattern in patterns:
                if pattern in text_lower:
                    return category, 0.95
        
        return None, 0.0
    
    def classify(self, text: str, return_confidence: bool = False) -> any:
        """
        Classify a single transaction description with optional confidence.
        
        Args:
            text: Raw transaction description
            return_confidence: If True, return (category, confidence) tuple
            
        Returns:
            str: Predicted category, or
            Tuple[str, float]: (category, confidence) if return_confidence=True
        """
        # NLP cleaning
        cleaned = clean_text(text)
        
        if not cleaned:
            return ('Others', 0.5) if return_confidence else 'Others'
        
        # Try rule-based classification first
        rule_category, rule_confidence = self.apply_rules(cleaned)
        if rule_category:
            return (rule_category, rule_confidence) if return_confidence else rule_category
        
        # ML-based classification
        try:
            # TF-IDF vectorization
            vector = self.vectorizer.transform([cleaned])
            
            # SVM prediction
            category = self.model.predict(vector)[0]
            
            # Get confidence score (decision function)
            if hasattr(self.model, 'decision_function'):
                decision_scores = self.model.decision_function(vector)[0]
                # Convert to probability-like score (0-1)
                max_score = np.max(decision_scores)
                confidence = 1 / (1 + np.exp(-max_score))  # Sigmoid
                confidence = min(0.95, max(0.5, confidence))  # Clamp between 0.5-0.95
            else:
                confidence = 0.75  # Default confidence
            
            return (category, confidence) if return_confidence else category
            
        except Exception as e:
            print(f"⚠️  Classification error: {e}")
            return ('Others', 0.5) if return_confidence else 'Others'
    
    def classify_batch(self, texts: List[str], return_confidence: bool = False) -> any:
        """
        Classify multiple transaction descriptions efficiently.
        
        Args:
            texts: List of raw transaction descriptions
            return_confidence: If True, return list of (category, confidence) tuples
            
        Returns:
            List[str]: List of predicted categories, or
            List[Tuple[str, float]]: List of (category, confidence) tuples
        """
        if not texts:
            return []
        
        results = []
        
        # NLP cleaning
        cleaned_texts = [clean_text(text) for text in texts]
        
        # Separate rule-based and ML-based classifications
        ml_indices = []
        ml_texts = []
        
        for i, (original, cleaned) in enumerate(zip(texts, cleaned_texts)):
            if not cleaned:
                results.append(('Others', 0.5) if return_confidence else 'Others')
                continue
            
            # Try rule-based first
            rule_category, rule_confidence = self.apply_rules(cleaned)
            if rule_category:
                results.append((rule_category, rule_confidence) if return_confidence else rule_category)
            else:
                # Mark for ML classification
                ml_indices.append(i)
                ml_texts.append(cleaned)
                results.append(None)  # Placeholder
        
        # Batch ML classification for remaining texts
        if ml_texts:
            try:
                # TF-IDF vectorization (batch)
                vectors = self.vectorizer.transform(ml_texts)
                
                # SVM prediction (batch)
                categories = self.model.predict(vectors)
                
                # Get confidence scores
                if hasattr(self.model, 'decision_function'):
                    decision_scores = self.model.decision_function(vectors)
                    max_scores = np.max(decision_scores, axis=1)
                    confidences = 1 / (1 + np.exp(-max_scores))  # Sigmoid
                    confidences = np.clip(confidences, 0.5, 0.95)
                else:
                    confidences = [0.75] * len(categories)
                
                # Fill in ML results
                for idx, ml_idx in enumerate(ml_indices):
                    if return_confidence:
                        results[ml_idx] = (categories[idx], float(confidences[idx]))
                    else:
                        results[ml_idx] = categories[idx]
                        
            except Exception as e:
                print(f"⚠️  Batch classification error: {e}")
                # Fill remaining with 'Others'
                for ml_idx in ml_indices:
                    results[ml_idx] = ('Others', 0.5) if return_confidence else 'Others'
        
        return results
    
    def classify_with_details(self, text: str) -> Dict:
        """
        Classify with detailed information including features and confidence.
        
        Args:
            text: Raw transaction description
            
        Returns:
            Dictionary with classification details
        """
        # Extract features
        features = enhance_features(text)
        
        # Classify with confidence
        category, confidence = self.classify(text, return_confidence=True)
        
        # Get category hints
        hints = get_category_hints(features['cleaned_text'])
        
        return {
            'category': category,
            'confidence': round(confidence, 3),
            'cleaned_text': features['cleaned_text'],
            'merchant': features['merchant'],
            'category_hints': hints,
            'features': {
                'word_count': features['word_count'],
                'has_upi': features['has_upi'],
                'has_transfer': features['has_transfer'],
                'has_atm': features['has_atm'],
            }
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            'model_type': type(self.model).__name__,
            'vectorizer_type': type(self.vectorizer).__name__,
            'vocabulary_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0,
            'categories': list(self.model.classes_) if hasattr(self.model, 'classes_') else [],
            'rule_based_categories': list(self.rule_patterns.keys()),
        }


# Singleton instance for reuse
_classifier_instance = None

def get_classifier() -> TransactionClassifier:
    """Get or create classifier singleton instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TransactionClassifier()
    return _classifier_instance


def classify_text(text: str) -> str:
    """
    Convenience function for single text classification.
    """
    classifier = get_classifier()
    return classifier.classify(text)


def classify_batch(texts: List[str]) -> List[str]:
    """
    Convenience function for batch text classification.
    """
    classifier = get_classifier()
    return classifier.classify_batch(texts)
