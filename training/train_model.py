
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import os
import sys
import time
import numpy as np

# Add parent directory to path to import text_cleaner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from text_cleaner import clean_text

def train_model():
    """
    Train TF-IDF + Linear SVM model for transaction classification.
    """
    print("=" * 50)
    print("Starting Model Training Pipeline")
    print("=" * 50)
    
    # Load dataset
    print("\n[1/6] Loading dataset...")
    df = pd.read_csv('dataset.csv')
    print(f"   ✓ Loaded {len(df)} transactions")
    print(f"   ✓ Categories: {df['category'].unique().tolist()}")
    
    # Clean text data
    print("\n[2/6] Cleaning text data...")
    df['cleaned_description'] = df['description'].apply(clean_text)
    print(f"   ✓ Text cleaned")
    print(f"   Example: '{df['description'].iloc[0]}' → '{df['cleaned_description'].iloc[0]}'")
    
    # Split data
    print("\n[3/6] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_description'], 
        df['category'], 
        test_size=0.2, 
        random_state=42,
        stratify=df['category']
    )
    print(f"   ✓ Train: {len(X_train)} samples")
    print(f"   ✓ Test: {len(X_test)} samples")
    
    # Create TF-IDF vectorizer with enhanced parameters
    print("\n[4/6] Creating TF-IDF vectors...")
    vectorizer = TfidfVectorizer(
        max_features=150,  # Increased from 100 for better feature capture
        ngram_range=(1, 3),  # Added trigrams for better context
        min_df=1,
        max_df=0.95,  # Ignore terms that appear in >95% of documents
        sublinear_tf=True,  # Use log scaling for term frequency
        strip_accents='unicode',
        lowercase=True
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"   ✓ Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"   ✓ Feature matrix shape: {X_train_tfidf.shape}")
    print(f"   ✓ N-gram range: {vectorizer.ngram_range}")
    
    # Train Linear SVM with enhanced parameters
    print("\n[5/6] Training Linear SVM...")
    model = LinearSVC(
        random_state=42,
        max_iter=2000,  # Increased for better convergence
        C=1.0,  # Regularization parameter
        class_weight='balanced',  # Handle class imbalance
        dual=False  # Faster for n_samples > n_features
    )
    model.fit(X_train_tfidf, y_train)
    print(f"   ✓ Model trained with {len(model.classes_)} categories")
    
    # Evaluate
    print("\n[6/6] Evaluating model...")
    
    # Measure prediction time
    start_time = time.time()
    y_pred = model.predict(X_test_tfidf)
    prediction_time = time.time() - start_time
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   ✓ Accuracy: {accuracy * 100:.2f}%")
    print(f"   ✓ Prediction time: {prediction_time*1000:.2f}ms for {len(X_test)} samples")
    print(f"   ✓ Avg time per sample: {(prediction_time/len(X_test))*1000:.2f}ms")
    
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Show per-category accuracy
    print("\n   Per-Category Performance:")
    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
    for i, category in enumerate(model.classes_):
        correct = cm[i, i]
        total = cm[i, :].sum()
        cat_accuracy = (correct / total * 100) if total > 0 else 0
        print(f"   • {category:15s}: {cat_accuracy:5.1f}% ({correct}/{total} samples)")
    
    # Show most confused pairs
    print("\n   Most Confused Categories:")
    confused_pairs = []
    for i in range(len(model.classes_)):
        for j in range(len(model.classes_)):
            if i != j and cm[i, j] > 0:
                confused_pairs.append((model.classes_[i], model.classes_[j], cm[i, j]))
    
    confused_pairs.sort(key=lambda x: x[2], reverse=True)
    for true_cat, pred_cat, count in confused_pairs[:5]:
        print(f"   • {true_cat} → {pred_cat}: {count} times")
    
    # Save models
    print("\nSaving models...")
    os.makedirs('../app/models', exist_ok=True)
    
    with open('../app/models/svm_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("   ✓ Saved: svm_model.pkl")
    
    with open('../app/models/vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    print("   ✓ Saved: vectorizer.pkl")
    
    print("\n" + "=" * 50)
    print("Training Complete!")
    print("=" * 50)

if __name__ == "__main__":
    train_model()
