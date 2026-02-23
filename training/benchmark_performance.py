"""
Performance Benchmark for Enhanced ML Classifier
Tests speed and accuracy improvements
"""

import sys
import os
import time
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.classifier import get_classifier
from app.utils.text_cleaner import clean_text, enhance_features

def benchmark_classification_speed():
    """Benchmark classification speed"""
    print("=" * 70)
    print("CLASSIFICATION SPEED BENCHMARK")
    print("=" * 70)
    
    classifier = get_classifier()
    
    # Test samples
    test_samples = [
        "ZOMATO ORDER FOOD DELIVERY",
        "UPI TRANSFER TO RAHUL SHARMA",
        "ATM WITHDRAWAL HDFC BANK",
        "AMAZON SHOPPING ONLINE",
        "ELECTRICITY BILL PAYMENT",
        "UBER TRIP BANGALORE",
        "NETFLIX SUBSCRIPTION MONTHLY",
        "SALARY CREDITED FROM COMPANY",
        "USHA MARTIN UNIVERSITY FEE PAYMENT",
        "CASHBACK FROM PHONEPE"
    ] * 10  # 100 samples
    
    # Single classification benchmark
    print("\n1. Single Classification:")
    start = time.time()
    for sample in test_samples[:10]:
        category = classifier.classify(sample)
    single_time = time.time() - start
    print(f"   • Time for 10 samples: {single_time*1000:.2f}ms")
    print(f"   • Avg per sample: {(single_time/10)*1000:.2f}ms")
    
    # Batch classification benchmark
    print("\n2. Batch Classification:")
    start = time.time()
    categories = classifier.classify_batch(test_samples)
    batch_time = time.time() - start
    print(f"   • Time for 100 samples: {batch_time*1000:.2f}ms")
    print(f"   • Avg per sample: {(batch_time/100)*1000:.2f}ms")
    print(f"   • Speedup: {single_time/batch_time:.1f}x faster")
    
    # Classification with confidence
    print("\n3. Classification with Confidence:")
    start = time.time()
    for sample in test_samples[:10]:
        category, confidence = classifier.classify(sample, return_confidence=True)
    conf_time = time.time() - start
    print(f"   • Time for 10 samples: {conf_time*1000:.2f}ms")
    print(f"   • Avg per sample: {(conf_time/10)*1000:.2f}ms")
    
    # Detailed classification
    print("\n4. Detailed Classification:")
    start = time.time()
    for sample in test_samples[:10]:
        details = classifier.classify_with_details(sample)
    detail_time = time.time() - start
    print(f"   • Time for 10 samples: {detail_time*1000:.2f}ms")
    print(f"   • Avg per sample: {(detail_time/10)*1000:.2f}ms")

def benchmark_text_cleaning():
    """Benchmark text cleaning speed"""
    print("\n" + "=" * 70)
    print("TEXT CLEANING BENCHMARK")
    print("=" * 70)
    
    test_texts = [
        "UPI/ZOMATO/ORDER/REF:98374628374/DATE:12-01-2024/TIME:14:30:45",
        "PAID TO AMAZON.IN RS 2499.00 TXN ID 837462837462",
        "NEFT TRANSFER TO RAHUL SHARMA AC NO 1234567890 REF NO 98374",
        "ATM WDL HDFC BANK ATM ID 8374 DATE 12/01/2024 TIME 10:30 AM",
        "ELECTRICITY BILL PAYMENT MSEB BILL NO 837462 RS 1500.00"
    ] * 20  # 100 samples
    
    # Basic cleaning
    print("\n1. Basic Text Cleaning:")
    start = time.time()
    cleaned = [clean_text(text) for text in test_texts]
    clean_time = time.time() - start
    print(f"   • Time for 100 samples: {clean_time*1000:.2f}ms")
    print(f"   • Avg per sample: {(clean_time/100)*1000:.2f}ms")
    
    # Enhanced feature extraction
    print("\n2. Enhanced Feature Extraction:")
    start = time.time()
    features = [enhance_features(text) for text in test_texts[:10]]
    feature_time = time.time() - start
    print(f"   • Time for 10 samples: {feature_time*1000:.2f}ms")
    print(f"   • Avg per sample: {(feature_time/10)*1000:.2f}ms")

def test_accuracy_improvements():
    """Test accuracy with enhanced preprocessing"""
    print("\n" + "=" * 70)
    print("ACCURACY TEST WITH REAL EXAMPLES")
    print("=" * 70)
    
    classifier = get_classifier()
    
    # Test cases with expected categories
    test_cases = [
        ("ZOMATO ORDER FOOD DELIVERY", "Food"),
        ("SWIGGY INSTAMART GROCERY", "Food"),
        ("UBER TRIP BANGALORE", "Transport"),
        ("OLA CABS RIDE PAYMENT", "Transport"),
        ("AMAZON SHOPPING ONLINE", "Shopping"),
        ("FLIPKART ORDER DELIVERY", "Shopping"),
        ("ELECTRICITY BILL PAYMENT", "Utilities"),
        ("MOBILE RECHARGE AIRTEL", "Utilities"),
        ("ATM WITHDRAWAL HDFC", "ATM"),
        ("CASH WDL SBI ATM", "ATM"),
        ("UPI TRANSFER TO RAHUL", "Transfer"),
        ("NEFT TO PRIYA SHARMA", "Transfer"),
        ("NETFLIX SUBSCRIPTION", "Entertainment"),
        ("PRIME VIDEO MONTHLY", "Entertainment"),
        ("SALARY CREDITED", "Income"),
        ("BONUS RECEIVED", "Income"),
        ("USHA MARTIN UNIVERSITY FEE", "Education"),
        ("COLLEGE TUITION PAYMENT", "Education"),
        ("CASHBACK FROM PHONEPE", "Cashback"),
        ("PAYTM CASHBACK RECEIVED", "Cashback"),
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("\nTest Results:")
    print("-" * 70)
    
    for description, expected in test_cases:
        predicted, confidence = classifier.classify(description, return_confidence=True)
        is_correct = predicted == expected
        correct += is_correct
        
        status = "✓" if is_correct else "✗"
        print(f"{status} {description[:40]:40s} | Expected: {expected:12s} | Got: {predicted:12s} | Conf: {confidence:.2f}")
    
    accuracy = (correct / total) * 100
    print("-" * 70)
    print(f"\nAccuracy: {accuracy:.1f}% ({correct}/{total} correct)")

def show_model_info():
    """Show model information"""
    print("\n" + "=" * 70)
    print("MODEL INFORMATION")
    print("=" * 70)
    
    classifier = get_classifier()
    info = classifier.get_model_info()
    
    print(f"\nModel Type: {info['model_type']}")
    print(f"Vectorizer Type: {info['vectorizer_type']}")
    print(f"Vocabulary Size: {info['vocabulary_size']}")
    print(f"\nCategories ({len(info['categories'])}):")
    for cat in info['categories']:
        print(f"  • {cat}")
    print(f"\nRule-Based Categories ({len(info['rule_based_categories'])}):")
    for cat in info['rule_based_categories']:
        print(f"  • {cat}")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ENHANCED ML CLASSIFIER PERFORMANCE BENCHMARK")
    print("=" * 70)
    
    show_model_info()
    benchmark_text_cleaning()
    benchmark_classification_speed()
    test_accuracy_improvements()
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)
