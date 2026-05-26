"""
Database Manager for storing and retrieving cleaned transactions
"""

import pandas as pd
from sqlalchemy.orm import Session
from database import Transaction, UploadedFile, FinancialSummary, CategoryBreakdown
from datetime import datetime, timezone
import uuid


class DatabaseManager:
    """Manages database operations for cleaned transactions"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def store_cleaned_data(self, df: pd.DataFrame, file_info: dict, cleaning_stats: dict) -> str:
        """
        Store cleaned transactions in the database.

        Args:
            df: Cleaned DataFrame with description and amount
            file_info: File metadata (filename, size, format)
            cleaning_stats: Cleaning statistics

        Returns:
            file_id: Unique identifier for this upload
        """
        file_id = str(uuid.uuid4())

        print(f"\n💾 Storing cleaned data in database...")
        print(f"   File ID: {file_id}")

        original_rows = cleaning_stats.get('original_rows', 0)
        cleaned_rows = cleaning_stats.get('cleaned_rows', 0)
        removed_rows = cleaning_stats.get('removed_rows', 0)

        retention_rate = round(
            (cleaned_rows / original_rows * 100), 1
        ) if original_rows > 0 else 0.0

        uploaded_file = UploadedFile(
            id=file_id,
            filename=file_info['filename'],
            file_format=file_info['format'],
            file_size=file_info['size'],
            original_rows=original_rows,
            cleaned_rows=cleaned_rows,
            removed_rows=removed_rows,
            retention_rate=retention_rate,
            quality_score=cleaning_stats.get('quality_score', 0),
            processing_time=cleaning_stats.get('processing_time', 0),
            uploaded_at=datetime.now(timezone.utc),
            processed=False
        )
        self.db.add(uploaded_file)

        # Build transaction objects and bulk-insert
        transactions = [
            Transaction(
                file_id=file_id,
                description=row['description'],
                amount=float(row['amount']),
                transaction_type=row.get('transaction_type', None),
                category=None,   # Filled after ML classification
                confidence=None,
                created_at=datetime.now(timezone.utc)
            )
            for _, row in df.iterrows()
        ]

        try:
            self.db.add_all(transactions)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        print(f"   ✅ Stored {len(transactions)} transactions")
        print(f"   ✅ File metadata saved")

        return file_id

    def retrieve_cleaned_data(self, file_id: str) -> pd.DataFrame:
        """
        Retrieve cleaned transactions from the database.

        Args:
            file_id: Unique file identifier

        Returns:
            DataFrame with description, amount, and transaction_type columns
        """
        print(f"\n📥 Retrieving cleaned data from database...")
        print(f"   File ID: {file_id}")

        transactions = self.db.query(Transaction).filter(
            Transaction.file_id == file_id
        ).all()

        if not transactions:
            raise ValueError(f"No transactions found for file_id: {file_id}")

        df = pd.DataFrame({
            'id': [t.id for t in transactions],
            'description': [t.description for t in transactions],
            'amount': [t.amount for t in transactions],
            'transaction_type': [t.transaction_type for t in transactions]
        })

        print(f"   ✅ Retrieved {len(df)} transactions")

        return df

    def update_classifications(self, file_id: str, df: pd.DataFrame):
        """
        Update transaction categories after ML classification.

        Args:
            file_id: Unique file identifier
            df: DataFrame with an 'id' column (DB primary key), 'category',
                and optionally 'confidence'
        """
        print(f"\n🔄 Updating classifications in database...")
        print("process is done ");
        if 'id' not in df.columns:
            # Fallback: match by description + amount (less reliable)
            transactions = self.db.query(Transaction).filter(
                Transaction.file_id == file_id
            ).all()

            updated_count = 0
            for transaction in transactions:
                match = df[
                    (df['description'] == transaction.description) &
                    (df['amount'] == transaction.amount)
                ]
                if not match.empty:
                    transaction.category = match.iloc[0]['category']
                    if 'confidence' in match.columns:
                        transaction.confidence = float(match.iloc[0]['confidence'])
                    updated_count += 1
        else:
            # Preferred path: match by DB primary key (exact, no ambiguity)
            id_to_row = df.set_index('id')
            transactions = self.db.query(Transaction).filter(
                Transaction.file_id == file_id
            ).all()

            updated_count = 0
            for transaction in transactions:
                if transaction.id in id_to_row.index:
                    row = id_to_row.loc[transaction.id]
                    transaction.category = row['category']
                    if 'confidence' in df.columns:
                        transaction.confidence = float(row['confidence'])
                    updated_count += 1

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        print(f"   ✅ Updated {updated_count} classifications")

    def store_summary(self, file_id: str, summary: dict):
        """
        Store financial summary in the database.

        Args:
            file_id: Unique file identifier
            summary: Financial summary dictionary
        """
        print(f"\n💾 Storing financial summary...")

        financial_summary = FinancialSummary(
            file_id=file_id,
            income=summary['income'],
            expense=summary['expense'],
            remaining_balance=summary['remaining_balance'],
            transaction_count=summary.get('transactionCount', 0),
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(financial_summary)

        for category, amount in summary['categories'].items():
            category_breakdown = CategoryBreakdown(
                file_id=file_id,
                category=category,
                amount=amount,
                transaction_count=0,
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(category_breakdown)

        # Mark file as processed
        uploaded_file = self.db.query(UploadedFile).filter(
            UploadedFile.id == file_id
        ).first()
        if uploaded_file:
            uploaded_file.processed = True

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        print(f"   ✅ Summary stored successfully")

    def get_file_history(self, limit: int = 10):
        """
        Get recent file upload history.

        Args:
            limit: Number of recent files to retrieve

        Returns:
            List of file metadata dicts
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
        Retrieve stored summary by file_id.

        Args:
            file_id: Unique file identifier

        Returns:
            Summary dictionary or None
        """
        summary = self.db.query(FinancialSummary).filter(
            FinancialSummary.file_id == file_id
        ).first()

        if not summary:
            return None

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


