#!/usr/bin/env python3
"""
Analyze Apple financial accounts in Monarch Money.
"""

import asyncio
import json
import os
from typing import Dict, List, Any

from monarchmoney import MonarchMoney

APPLE_PROVIDERS = ["Apple Card", "Apple Cash", "Apple Savings"]

async def analyze_apple_accounts():
    """Analyze Apple financial accounts and their balances."""
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
        print("\n🔄 Analyzing Apple accounts...")
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

        total_balance = 0

        print("\n" + "="*60)
        for account in apple_accounts:
            balance = account.get('currentBalance', 0)
            if balance is None:
                balance = 0

            total_balance += balance

            print(f"\n📊 {account.get('displayName', 'Unknown')}")
            print(f"   Type: {account.get('type', {}).get('display', 'Unknown')}")
            print(f"   Balance: ${balance:,.2f}")
            print(f"   Institution: {account.get('institution', {}).get('name', 'Unknown')}")
            print(f"   Last Updated: {account.get('displayLastUpdatedAt', 'Unknown')}")
            print(f"   Account ID: {account.get('id', 'Unknown')}")

            # Save account data
            account_data = {
                'id': account.get('id'),
                'name': account.get('displayName'),
                'type': account.get('type', {}).get('name'),
                'balance': balance,
                'institution': account.get('institution', {}).get('name'),
                'last_updated': account.get('displayLastUpdatedAt'),
            }

            filename = f"data/exports/{account.get('displayName', 'Unknown').replace(' ', '_')}.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(account_data, f, indent=2)
            print(f"   Data saved to: {filename}")

        print("\n" + "="*60)
        print(f"\n💰 Total Apple Account Balance: ${total_balance:,.2f}")

        return apple_accounts

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("- Token might be expired (try getting a fresh one)")
        print("- Network connection issues")
        print("- API changes")
        return None

if __name__ == "__main__":
    asyncio.run(analyze_apple_accounts())
