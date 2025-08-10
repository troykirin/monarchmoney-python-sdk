#!/usr/bin/env python3
"""
Analyze transactions from Apple financial accounts.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

from monarchmoney import MonarchMoney

APPLE_PROVIDERS = ["Apple Card", "Apple Cash", "Apple Savings"]

async def analyze_apple_transactions(days: int = 30):
    """
    Analyze transactions from Apple financial accounts.
    
    Args:
        days: Number of days of transaction history to analyze (default: 30)
    """
    token = os.getenv('MONARCH_TOKEN')
    
    if not token:
        print("⚠️  No MONARCH_TOKEN environment variable found.")
        print("\nTo get your token:")
        print("1. Log into https://app.monarchmoney.com")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Network tab")
        print("4. Look for any GraphQL request")
        print("5. Check the Request Headers for 'Authorization: Token YOUR_TOKEN_HERE'")
        print("\nThen set it with: export MONARCH_TOKEN='your_token_here'")
        return None

    mm = MonarchMoney(token=token)
    
    try:
        # Get Apple accounts
        print("\n🔄 Finding Apple accounts...")
        accounts = await mm.get_accounts()
        
        apple_accounts = []
        for account in accounts.get('accounts', []):
            institution = account.get('institution', {}).get('name', '')
            if any(provider in institution for provider in APPLE_PROVIDERS):
                apple_accounts.append(account)

        if not apple_accounts:
            print("\n❌ No Apple financial accounts found.")
            return None

        print(f"\n✅ Found {len(apple_accounts)} Apple accounts")
        
        # Get transactions for each account
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        print(f"\n🔄 Analyzing transactions from {start_date} to {end_date}...")
        
        for account in apple_accounts:
            account_id = account.get('id')
            account_name = account.get('displayName', 'Unknown')
            
            print(f"\n📊 {account_name}")
            
            transactions = await mm.get_transactions(
                start_date=start_date,
                end_date=end_date,
                account_ids=[account_id],
                limit=1000
            )
            
            transaction_list = transactions.get('allTransactions', {}).get('results', [])
            if not transaction_list:
                print("   No transactions found")
                continue
            
            print(f"   Found {len(transaction_list)} transactions")
            
            # Analyze transactions
            total_amount = 0
            categories = {}
            merchants = {}
            
            for transaction in transaction_list:
                amount = transaction.get('amount', 0)
                total_amount += amount
                
                # Track categories
                category = transaction.get('category', {}).get('name', 'Uncategorized')
                categories[category] = categories.get(category, 0) + amount
                
                # Track merchants
                merchant = transaction.get('merchant', {}).get('name', 'Unknown')
                merchants[merchant] = merchants.get(merchant, 0) + amount
            
            print(f"   Total Amount: ${total_amount:,.2f}")
            
            # Save transaction data
            transaction_data = {
                'account_id': account_id,
                'account_name': account_name,
                'start_date': start_date,
                'end_date': end_date,
                'total_amount': total_amount,
                'transaction_count': len(transaction_list),
                'categories': categories,
                'merchants': merchants,
                'transactions': transaction_list
            }
            
            filename = f"data/exports/{account_name.replace(' ', '_')}_transactions.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(transaction_data, f, indent=2)
            print(f"   Data saved to: {filename}")
            
            # Show top categories
            print("\n   Top Categories:")
            sorted_categories = sorted(categories.items(), key=lambda x: abs(x[1]), reverse=True)
            for category, amount in sorted_categories[:5]:
                print(f"   - {category}: ${amount:,.2f}")
            
            # Show top merchants
            print("\n   Top Merchants:")
            sorted_merchants = sorted(merchants.items(), key=lambda x: abs(x[1]), reverse=True)
            for merchant, amount in sorted_merchants[:5]:
                print(f"   - {merchant}: ${amount:,.2f}")
            
            print("\n" + "-"*40)
        
        return apple_accounts
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("- Token might be expired (try getting a fresh one)")
        print("- Network connection issues")
        print("- API changes")
        return None

if __name__ == "__main__":
    asyncio.run(analyze_apple_transactions())
