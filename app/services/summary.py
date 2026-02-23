
import pandas as pd
from collections import defaultdict

def calculate_summary(transactions_df):
    """
    Calculate financial summary from classified transactions.
    ALL CREDIT transactions go to income, ALL DEBIT transactions go to expense.
    
    Args:
        transactions_df (DataFrame): DataFrame with columns: description, category, amount, transaction_type
        
    Returns:
        dict: Financial summary in JSON format
    """
    total_income = 0
    total_expense = 0
    categories = {}
    
    # Check if transaction_type column exists
    has_transaction_type = 'transaction_type' in transactions_df.columns
    
    if has_transaction_type:
        # Use transaction_type to determine income vs expense
        # ALL credits → income, ALL debits → expense
        credit_transactions = transactions_df[transactions_df['transaction_type'] == 'credit']
        debit_transactions = transactions_df[transactions_df['transaction_type'] == 'debit']
        
        total_income = float(credit_transactions['amount'].sum())
        total_expense = float(debit_transactions['amount'].sum())
        
        # Group expenses by category
        if len(debit_transactions) > 0:
            category_groups = debit_transactions.groupby('category')
            for category, group in category_groups:
                total = float(group['amount'].sum())
                categories[category] = round(total, 2)
    else:
        # Fallback: Use category-based logic (old behavior)
        income_categories = ['Income', 'Cashback']
        
        category_groups = transactions_df.groupby('category')
        
        for category, group in category_groups:
            total = float(group['amount'].sum())
            
            if category in income_categories:
                total_income += total
            else:
                total_expense += total
                categories[category] = round(total, 2)
    
    # Calculate balance (never show negative, show 0 instead)
    balance = total_income - total_expense
    remaining_balance = max(0, balance)
    
    # Build JSON structure
    summary = {
        'income': round(total_income, 2),
        'expense': round(total_expense, 2),
        'remaining_balance': round(remaining_balance, 2),
        'categories': categories
    }
    
    return summary

def generate_insights(summary):
    """
    Generate human-readable insights from summary.
    
    Args:
        summary (dict): Financial summary
        
    Returns:
        list: List of insight strings
    """
    insights = []
    
    # Top spending category
    if summary['categories']:
        top_category = max(summary['categories'].items(), key=lambda x: x[1])
        insights.append(f"Highest spending: {top_category[0]} (₹{top_category[1]})")
    
    # Balance status
    if summary['remaining_balance'] > 0:
        insights.append(f"Positive balance: ₹{summary['remaining_balance']}")
    elif summary['remaining_balance'] < 0:
        insights.append(f"Deficit: ₹{abs(summary['remaining_balance'])}")
    else:
        insights.append("Balanced budget")
    
    # Expense info
    insights.append(f"Total expense: ₹{summary['expense']}")
    
    return insights

def summarize_text(text):
    """
    Legacy function - kept for compatibility.
    """
    return f"Summary: {text[:100]}..."
