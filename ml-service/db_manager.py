"""
Database Manager for storing and retrieving cleaned transactions
"""

import pandas as pd
from sqlalchemy.orm import Session
from database import Transaction, UploadedFile, FinancialSummary, CategoryBreakdown
from datetime import datetime
import uuid


class DatabaseManager:
    """Manages database operations for cleaned transactions"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def store_cleaned_data(self, df: pd.DataFrame, file_info: dict, cleaning_stats: dict) -> str:
        """
        Store cleaned transactions in PostgreSQL
        
        Args:
            df: Cleaned DataFrame with description and amount
            file_info: File metadata (filename, size, format)
            cleaning_stats: Cleaning statistics
            
        Returns:
            file_id: Unique identifier for this upload
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        print(f"\n💾 Storing cleaned data in PostgreSQL...")
        print(f"   File ID: {file_id}")
        
        # Store file metadata
        uploaded_file = UploadedFile(
            id=file_id,
            filename=file_info['filename'],
            file_format=file_info['format'],
            file_size=file_info['size'],
            original_rows=cleaning_stats['original_rows'],
            cleaned_rows=cleaning_stats['cleaned_rows'],
            removed_rows=cleaning_stats['removed_rows'],
            retention_rate=round(
                (cleaning_stats['cleaned_rows'] / cleaning_stats['original_rows'] * 100), 1
            ) if cleaning_stats['original_rows'] > 0 else 0,
            quality_score=cleaning_stats.get('quality_score', 0),
            processing_time=cleaning_stats.get('processing_time', 0),
            uploaded_at=datetime.utcnow(),
            processed=False
        )
        self.db.add(uploaded_file)
        
        # Store transactions (bulk insert for performance)
        transactions = []
        for idx, row in df.iterrows():
            transaction = Transaction(
                file_id=file_id,
                description=row['description'],
                amount=float(row['amount']),
                transaction_type=row.get('transaction_type', None),  # Store transaction_type if available
                category=None,  # Will be filled after ML classification
                confidence=None,
                created_at=datetime.utcnow()
            )
            transactions.append(transaction)
        
        self.db.bulk_save_objects(transactions)
        self.db.commit()
        
        print(f"   ✅ Stored {len(transactions)} transactions")
        print(f"   ✅ File metadata saved")
        
        return file_id
    
    def retrieve_cleaned_data(self, file_id: str) -> pd.DataFrame:
        """
        Retrieve cleaned transactions from PostgreSQL
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            DataFrame with description and amount columns
        """
        print(f"\n📥 Retrieving cleaned data from PostgreSQL...")
        print(f"   File ID: {file_id}")
        
        # Query transactions
        transactions = self.db.query(Transaction).filter(
            Transaction.file_id == file_id
        ).all()
        
        if not transactions:
            raise ValueError(f"No transactions found for file_id: {file_id}")
        
        # Convert to DataFrame
        data = {
            'description': [t.description for t in transactions],
            'amount': [t.amount for t in transactions],
            'transaction_type': [t.transaction_type for t in transactions]  # Retrieve transaction_type
        }
        df = pd.DataFrame(data)
        
        # Remove rows where transaction_type is None (shouldn't happen, but just in case)
        # Actually, keep them - they'll be detected later from description
        
        print(f"   ✅ Retrieved {len(df)} transactions")
        
        return df
    
    def update_classifications(self, file_id: str, df: pd.DataFrame):
        """
        Update transaction categories after ML classification
        
        Args:
            file_id: Unique file identifier
            df: DataFrame with description, amount, and category columns
        """
        print(f"\n🔄 Updating classifications in PostgreSQL...")
        
        # Get all transactions for this file
        transactions = self.db.query(Transaction).filter(
            Transaction.file_id == file_id
        ).all()
        
        # Update categories (match by description and amount)
        updated_count = 0
        for transaction in transactions:
            # Find matching row in DataFrame
            match = df[
                (df['description'] == transaction.description) & 
                (df['amount'] == transaction.amount)
            ]
            
            if not match.empty:
                transaction.category = match.iloc[0]['category']
                if 'confidence' in match.columns:
                    transaction.confidence = float(match.iloc[0]['confidence'])
                updated_count += 1
        
        self.db.commit()
        print(f"   ✅ Updated {updated_count} classifications")
    
    def store_summary(self, file_id: str, summary: dict):
        """
        Store financial summary in PostgreSQL
        
        Args:
            file_id: Unique file identifier
            summary: Financial summary dictionary
        """
        print(f"\n💾 Storing financial summary...")
        
        # Store main summary
        financial_summary = FinancialSummary(
            file_id=file_id,
            income=summary['income'],
            expense=summary['expense'],
            remaining_balance=summary['remaining_balance'],
            transaction_count=summary.get('transactionCount', 0),
            created_at=datetime.utcnow()
        )
        self.db.add(financial_summary)
        
        # Store category breakdown
        for category, amount in summary['categories'].items():
            category_breakdown = CategoryBreakdown(
                file_id=file_id,
                category=category,
                amount=amount,
                transaction_count=0,  # Can be calculated if needed
                created_at=datetime.utcnow()
            )
            self.db.add(category_breakdown)
        
        # Mark file as processed
        uploaded_file = self.db.query(UploadedFile).filter(
            UploadedFile.id == file_id
        ).first()
        if uploaded_file:
            uploaded_file.processed = True
        
        self.db.commit()
        print(f"   ✅ Summary stored successfully")
    
    def get_file_history(self, limit: int = 10):
        """
        Get recent file upload history
        
        Args:
            limit: Number of recent files to retrieve
            
        Returns:
            List of file metadata
        """
        files = self.db.query(UploadedFile).order_by(
            UploadedFile.uploaded_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'file_id': f.id,
                'filename': f.filename,
                'format': f.file_format,
                'cleaned_rows': f.cleaned_rows,
                'quality_score': f.quality_score,
                'uploaded_at': f.uploaded_at.isoformat(),
                'processed': f.processed
            }
            for f in files
        ]
    
    def get_summary_by_file_id(self, file_id: str):
        """
        Retrieve stored summary by file_id
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Summary dictionary
        """
        # Get main summary
        summary = self.db.query(FinancialSummary).filter(
            FinancialSummary.file_id == file_id
        ).first()
        
        if not summary:
            return None
        
        # Get category breakdown
        categories = self.db.query(CategoryBreakdown).filter(
            CategoryBreakdown.file_id == file_id
        ).all()
        
        return {
            'income': summary.income,
            'expense': summary.expense,
            'remaining_balance': summary.remaining_balance,
            'transaction_count': summary.transaction_count,
            'categories': {c.category: c.amount for c in categories}
        }


def get_db_manager(db_session: Session) -> DatabaseManager:
    """Factory function to create DatabaseManager instance"""
    return DatabaseManager(db_session)
