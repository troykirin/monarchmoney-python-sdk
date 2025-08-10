#!/usr/bin/env python3
"""
Migrate transactions from Apple Cash to Monarch Money.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any

from monarchmoney import MonarchMoney

async def migrate_apple_cash_transactions(input_file: str):
    """
    Migrate Apple Cash transactions to Monarch Money.

    Args:
        input_file: Path to JSON file containing Apple Cash transactions
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

    if not os.path.exists(input_file):
        print(f"\n❌ Input file not found: {input_file}")
        return None

    mm = MonarchMoney(token=token)

    try:
        # Load transactions from file
        print(f"\n🔄 Loading transactions from {input_file}...")
        with open(input_file, 'r') as f:
            data = json.load(f)

        transactions = data.get('transactions', [])
        if not transactions:
            print("\n❌ No transactions found in input file.")
            return None

        print(f"\n✅ Loaded {len(transactions)} transactions")

        # Get Apple Cash account
        print("\n🔄 Finding Apple Cash account...")
        accounts = await mm.get_accounts()

        apple_cash_account = None
        for account in accounts.get('accounts', []):
            institution = account.get('institution', {}).get('name', '')
            if "Apple Cash" in institution:
                apple_cash_account = account
                break

        if not apple_cash_account:
            print("\n❌ Apple Cash account not found.")
            return None

        account_id = apple_cash_account.get('id')
        print(f"\n✅ Found Apple Cash account: {apple_cash_account.get('displayName')}")

        # Get existing transactions to avoid duplicates
        print("\n🔄 Getting existing transactions...")
        existing = await mm.get_transactions(
            account_ids=[account_id],
            limit=1000
        )

        existing_transactions = existing.get('allTransactions', {}).get('results', [])
        existing_dates = set()
        for transaction in existing_transactions:
            date = transaction.get('date')
            amount = transaction.get('amount')
            merchant = transaction.get('merchant', {}).get('name', '')
            key = f"{date}|{amount}|{merchant}"
            existing_dates.add(key)

        print(f"\n✅ Found {len(existing_transactions)} existing transactions")

        # Migrate new transactions
        print("\n🔄 Migrating transactions...")
        migrated = 0
        skipped = 0

        for transaction in transactions:
            date = transaction.get('date')
            amount = transaction.get('amount')
            merchant = transaction.get('merchant', '')
            key = f"{date}|{amount}|{merchant}"

            if key in existing_dates:
                skipped += 1
                continue

            try:
                await mm.create_transaction(
                    date=date,
                    account_id=account_id,
                    amount=amount,
                    merchant_name=merchant,
                    category_id=transaction.get('category_id', ''),
                    notes=transaction.get('notes', ''),
                    update_balance=True
                )
                migrated += 1
                print(f"✅ Migrated: {date} - {merchant} - ${amount:,.2f}")
            except Exception as e:
                print(f"❌ Failed to migrate transaction: {e}")

        print(f"\n✅ Migration complete!")
        print(f"   Migrated: {migrated}")
        print(f"   Skipped (already exists): {skipped}")

        return {
            'migrated': migrated,
            'skipped': skipped,
            'total': len(transactions)
        }

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("- Token might be expired (try getting a fresh one)")
        print("- Network connection issues")
        print("- API changes")
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python migrate_apple_cash_transactions.py <input_file.json>")
        sys.exit(1)

    asyncio.run(migrate_apple_cash_transactions(sys.argv[1]))
