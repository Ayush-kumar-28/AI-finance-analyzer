"""
Online Learning Module
Allows the ML model to learn from new uploaded data
"""

import pandas as pd
import os
from datetime import datetime
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import sys

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from training.text_cleaner import clean_text

class OnlineLearner:
    """
    Handles online learning and model improvement
    """
    
    def __init__(self):
        # Get absolute paths relative to project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.new_data_path = os.path.join(project_root, "ml-service", "new_transactions.csv")
        self.training_data_path = os.path.join(project_root, "training", "dataset.csv")
        self.model_path = os.path.join(project_root, "app", "models", "svm_model.pkl")
        self.vectorizer_path = os.path.join(project_root, "app", "models", "vectorizer.pkl")
        self.min_samples_for_retrain = 50  # Retrain after 50 new samples
        
    def save_transaction(self, description, category, amount=None):
        """
        Save a new transaction for future training
        
        Args:
            description: Transaction description
            category: Predicted category
            amount: Transaction amount (optional)
        """
        # Create new data file if doesn't exist
        if not os.path.exists(self.new_data_path):
            df = pd.DataFrame(columns=['description', 'category', 'amount', 'timestamp'])
            df.to_csv(self.new_data_path, index=False)
        
        # Append new transaction
        new_row = {
            'description': description,
            'category': category,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }
        
        df = pd.read_csv(self.new_data_path)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.new_data_path, index=False)
        
        print(f"📝 Saved transaction: {description} → {category}")
        
        # Check if we should retrain
        if len(df) >= self.min_samples_for_retrain:
            print(f"✨ {len(df)} new samples collected. Ready for retraining!")
            return True
        
        return False
    
    def save_batch_transactions(self, transactions_df):
        """
        Save multiple transactions at once
        
        Args:
            transactions_df: DataFrame with columns [description, category, amount]
        """
        if not os.path.exists(self.new_data_path):
            df = pd.DataFrame(columns=['description', 'category', 'amount', 'timestamp'])
            df.to_csv(self.new_data_path, index=False)
        
        # Add timestamp
        transactions_df['timestamp'] = datetime.now().isoformat()
        
        # Append to existing data
        existing_df = pd.read_csv(self.new_data_path)
        combined_df = pd.concat([existing_df, transactions_df], ignore_index=True)
        combined_df.to_csv(self.new_data_path, index=False)
        
        print(f"📝 Saved {len(transactions_df)} transactions")
        
        # Check if we should retrain
        if len(combined_df) >= self.min_samples_for_retrain:
            print(f"✨ {len(combined_df)} new samples collected. Ready for retraining!")
            return True
        
        return False
    
    def get_new_samples_count(self):
        """Get count of new samples waiting for training"""
        if not os.path.exists(self.new_data_path):
            return 0
        
        df = pd.read_csv(self.new_data_path)
        return len(df)
    
    def merge_and_retrain(self):
        """
        Merge new data with training data and retrain model
        """
        print("\n" + "="*60)
        print("🔄 Starting Model Retraining")
        print("="*60)
        
        # Load existing training data
        training_df = pd.read_csv(self.training_data_path)
        print(f"📊 Current training data: {len(training_df)} samples")
        
        # Load new data
        if not os.path.exists(self.new_data_path):
            print("❌ No new data to train on")
            return False
        
        new_df = pd.read_csv(self.new_data_path)
        print(f"📊 New data: {len(new_df)} samples")
        
        if len(new_df) == 0:
            print("❌ No new data to train on")
            return False
        
        # Merge data (keep only description and category)
        new_training_data = new_df[['description', 'category']].copy()
        combined_df = pd.concat([training_df, new_training_data], ignore_index=True)
        
        # Remove duplicates
        combined_df = combined_df.drop_duplicates(subset=['description'])
        print(f"📊 Combined data: {len(combined_df)} samples (after removing duplicates)")
        
        # Clean text
        print("\n🧹 Cleaning text...")
        combined_df['cleaned_description'] = combined_df['description'].apply(clean_text)
        
        # Train new model
        print("\n🤖 Training new model...")
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2),
            min_df=1
        )
        
        X = vectorizer.fit_transform(combined_df['cleaned_description'])
        y = combined_df['category']
        
        # Train Linear SVM
        model = LinearSVC(random_state=42, max_iter=1000)
        model.fit(X, y)
        
        print(f"✅ Model trained on {len(combined_df)} samples")
        
        # Save updated training data
        combined_df[['description', 'category']].to_csv(self.training_data_path, index=False)
        print(f"✅ Updated training data saved: {self.training_data_path}")
        
        # Save new model
        with open(self.model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✅ Model saved: {self.model_path}")
        
        # Save new vectorizer
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
        print(f"✅ Vectorizer saved: {self.vectorizer_path}")
        
        # Archive new data (move to history)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        history_path = os.path.join(project_root, "ml-service", f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        new_df.to_csv(history_path, index=False)
        print(f"✅ New data archived: {history_path}")
        
        # Clear new data file
        pd.DataFrame(columns=['description', 'category', 'amount', 'timestamp']).to_csv(
            self.new_data_path, index=False
        )
        print(f"✅ New data file cleared")
        
        print("\n" + "="*60)
        print("🎉 Model Retraining Complete!")
        print("="*60)
        print(f"📊 Total training samples: {len(combined_df)}")
        print(f"📈 New samples added: {len(new_training_data)}")
        print(f"🎯 Categories: {y.nunique()}")
        print("="*60 + "\n")
        
        return True
    
    def auto_retrain_if_needed(self):
        """
        Automatically retrain if enough new samples collected
        """
        count = self.get_new_samples_count()
        
        if count >= self.min_samples_for_retrain:
            print(f"\n🔔 Auto-retraining triggered ({count} new samples)")
            return self.merge_and_retrain()
        
        return False

# Global instance
learner = OnlineLearner()
