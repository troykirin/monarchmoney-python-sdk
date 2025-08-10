#!/usr/bin/env python3
"""
Command-line interface for MonarchMoney Python SDK.
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Optional

from monarchmoney import MonarchMoney


class MonarchCLI:
    def __init__(self, token: Optional[str] = None):
        """Initialize MonarchMoney client."""
        self.mm = MonarchMoney(token=token)

    async def get_accounts(self) -> None:
        """Get and display account information."""
        try:
            print("\n🔄 Fetching accounts...")
            accounts = await self.mm.get_accounts()

            # Save accounts data
            with open("accounts_data.json", "w") as f:
                json.dump(accounts, f, indent=2)

            # Display summary
            account_list = accounts.get('accounts', [])
            print(f"\n✅ Successfully retrieved {len(account_list)} accounts")

            total_assets = 0
            total_liabilities = 0

            print("\n" + "="*60)
            for account in account_list:
                balance = account.get('currentBalance', 0)
                if balance is None:
                    balance = 0
                is_asset = account.get('isAsset', True)

                if is_asset:
                    total_assets += balance
                else:
                    total_liabilities += abs(balance)

                print(f"\n📊 {account.get('displayName', 'Unknown')}")
                print(f"   Type: {account.get('type', {}).get('display', 'Unknown')}")
                print(f"   Balance: ${balance:,.2f}")
                print(f"   Institution: {account.get('institution', {}).get('name', 'Unknown')}")
                print(f"   Asset: {'Yes' if is_asset else 'No (Liability)'}")

                # Show additional details if available
                if account.get('lastUpdatedAt'):
                    print(f"   Last Updated: {account.get('lastUpdatedAt')}")

            print("\n" + "="*60)
            print(f"\n💰 Total Assets: ${total_assets:,.2f}")
            print(f"💳 Total Liabilities: ${total_liabilities:,.2f}")
            print(f"📈 Net Worth: ${(total_assets - total_liabilities):,.2f}")

            print(f"\n✅ Data saved to accounts_data.json")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nPossible issues:")
            print("- Token might be expired (try getting a fresh one)")
            print("- Network connection issues")
            print("- API changes")
            sys.exit(1)

    async def get_transactions(self, limit: int = 5) -> None:
        """Get and display recent transactions."""
        try:
            print("\n🔄 Fetching recent transactions...")
            transactions = await self.mm.get_transactions(limit=limit)

            # Display recent transactions
            transaction_list = transactions.get('allTransactions', {}).get('results', [])
            print(f"\n✅ Successfully retrieved {len(transaction_list)} recent transactions")

            print("\n" + "="*60)
            for transaction in transaction_list:
                print(f"\n💸 {transaction.get('merchant', {}).get('name', 'Unknown')}")
                print(f"   Amount: ${transaction.get('amount', 0):,.2f}")
                print(f"   Date: {transaction.get('date', 'Unknown')}")
                print(f"   Account: {transaction.get('account', {}).get('displayName', 'Unknown')}")
                print(f"   Category: {transaction.get('category', {}).get('name', 'Unknown')}")
                if transaction.get('notes'):
                    print(f"   Notes: {transaction.get('notes')}")
            print("\n" + "="*60)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nPossible issues:")
            print("- Token might be expired (try getting a fresh one)")
            print("- Network connection issues")
            print("- API changes")
            sys.exit(1)


def get_token() -> str:
    """Get token from environment variable or prompt user."""
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

        token = input("\nPaste your token here (or press Enter to exit): ").strip()
        if not token:
            sys.exit(1)

    return token


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description="MonarchMoney CLI")
    parser.add_argument('command', choices=['accounts', 'transactions'],
                      help='Command to execute')
    parser.add_argument('--limit', type=int, default=5,
                      help='Number of transactions to fetch (default: 5)')
    args = parser.parse_args()

    token = get_token()
    cli = MonarchCLI(token=token)

    if args.command == 'accounts':
        asyncio.run(cli.get_accounts())
    elif args.command == 'transactions':
        asyncio.run(cli.get_transactions(limit=args.limit))


if __name__ == "__main__":
    main()
