#!/usr/bin/env python3
"""
MonarchMoney CLI Tool

A command-line interface for interacting with Monarch Money financial data.
Provides commands for authentication, data retrieval, and financial analysis.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

from . import MonarchMoney


class MonarchMoneyCLI:
    """Command-line interface for MonarchMoney API"""

    def __init__(self):
        self.session_file = ".mm/mm_session.pickle"
        self.cache_dir = "cache"
        self.mm: Optional[MonarchMoney] = None

    def get_session_ttl(self) -> float:
        """Get session TTL based on environment."""
        env = os.getenv("MONARCH_ENV", "development").lower()
        if env == "production":
            return 0.25  # 15 minutes
        else:
            return 1.0   # 1 hour for development

    def check_session(self) -> bool:
        """Check if session file exists and is still valid (within TTL)."""
        session_path = Path(self.session_file)
        ttl_hours = self.get_session_ttl()
        env = os.getenv("MONARCH_ENV", "development").lower()

        if not session_path.exists():
            print("ℹ️  No existing session file found")
            return False

        try:
            # Check session file modification time
            session_mtime = datetime.fromtimestamp(session_path.stat().st_mtime)
            now = datetime.now()
            age = now - session_mtime

            if age < timedelta(hours=ttl_hours):
                remaining = timedelta(hours=ttl_hours) - age
                print(f"✅ Valid session found (expires in {remaining}) [{env} mode]")
                return True
            else:
                print(f"⏰ Session expired (age: {age}), clearing... [{env} mode]")
                session_path.unlink()
                print("🗑️  Session cleared")
                return False

        except Exception as e:
            print(f"❌ Error checking session: {e}")
            print("🗑️  Clearing corrupted session...")
            session_path.unlink()
            return False

    def setup_cache(self, subdir: Optional[str] = None) -> Path:
        """Create cache directory with optional subdirectory."""
        if subdir:
            cache_path = Path(self.cache_dir) / subdir
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_path = Path(self.cache_dir) / timestamp

        cache_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created cache directory: {cache_path}")
        return cache_path

    async def ensure_authenticated(self, force_login: bool = False) -> bool:
        """Ensure we have a valid authenticated session."""
        if not self.mm:
            self.mm = MonarchMoney(session_file=self.session_file)

        # Check if we have a valid session
        has_valid_session = self.check_session() and not force_login

        # Only login if we don't have a valid session
        if not has_valid_session:
            print("🔐 Starting fresh login...")
            await self.mm.interactive_login(use_saved_session=False, save_session=True)
            print("✅ Login successful!")
            return True
        else:
            print("🔄 Using existing session...")
            # Try to load the existing session, fallback to fresh login if it fails
            try:
                self.mm.load_session(self.session_file)
                
                # Validate the session by making a test API call
                try:
                    await self.mm.get_subscription_details()
                    return True
                except Exception as api_error:
                    if "401" in str(api_error) or "Unauthorized" in str(api_error):
                        print("🔑 Session token expired, refreshing authentication...")
                        await self.mm.interactive_login(use_saved_session=False, save_session=True)
                        print("✅ Login successful!")
                        return True
                    else:
                        raise api_error
                        
            except Exception as e:
                print(f"❌ Failed to load session: {e}")
                print("🔐 Falling back to fresh login...")
                await self.mm.interactive_login(use_saved_session=False, save_session=True)
                print("✅ Login successful!")
                return True

    def save_json(self, data: Dict[Any, Any], filepath: Path, indent: int = None) -> None:
        """Save data to JSON file."""
        with open(filepath, "w") as outfile:
            json.dump(data, outfile, indent=indent)
        print(f"💾 Saved: {filepath}")

    async def cmd_login(self, args) -> None:
        """Handle login command."""
        await self.ensure_authenticated(force_login=args.force)
        print("✅ Authentication successful!")

    async def cmd_status(self, args) -> None:
        """Handle status command."""
        await self.ensure_authenticated()

        # Get subscription details
        subs = await self.mm.get_subscription_details()
        print("\n📊 Account Status:")
        print(f"   Subscription: {subs}")

    async def cmd_accounts(self, args) -> None:
        """Handle accounts command."""
        await self.ensure_authenticated()

        # Get accounts data
        accounts = await self.mm.get_accounts()

        if args.output:
            self.save_json(accounts, Path(args.output))
        else:
            print("\n🏦 Accounts:")
            for account in accounts.get("accounts", []):
                print(f"   {account.get('displayName', 'Unknown')}: ${account.get('currentBalance', 0):.2f}")

    async def cmd_transactions(self, args) -> None:
        """Handle transactions command."""
        await self.ensure_authenticated()

        # Get transactions
        transactions = await self.mm.get_transactions(limit=args.limit)

        if args.output:
            self.save_json(transactions, Path(args.output))
        else:
            print(f"\n💳 Recent {args.limit} Transactions:")
            for txn in transactions.get("allTransactions", {}).get("results", []):
                amount = txn.get("amount", 0)
                date = txn.get("date", "")
                description = txn.get("description", "Unknown")
                print(f"   {date}: {description} - ${amount:.2f}")

    async def cmd_budgets(self, args) -> None:
        """Handle budgets command."""
        await self.ensure_authenticated()

        # Get budgets
        budgets = await self.mm.get_budgets()

        if args.output:
            self.save_json(budgets, Path(args.output), indent=4)
        else:
            print("\n💰 Budgets:")
            for budget in budgets.get("budgetData", []):
                name = budget.get("name", "Unknown")
                amount = budget.get("amount", 0)
                spent = budget.get("spent", 0)
                print(f"   {name}: ${spent:.2f} / ${amount:.2f}")

    async def cmd_cashflow(self, args) -> None:
        """Handle cashflow command."""
        await self.ensure_authenticated()

        # Get cashflow data
        cashflow = await self.mm.get_cashflow(
            start_date=args.start_date,
            end_date=args.end_date
        )

        if args.output:
            self.save_json(cashflow, Path(args.output))
        else:
            print(f"\n📈 Cashflow ({args.start_date} to {args.end_date}):")
            for summary in cashflow.get("summary", []):
                income = summary.get("summary", {}).get("sumIncome", 0)
                expense = summary.get("summary", {}).get("sumExpense", 0)
                savings = summary.get("summary", {}).get("savings", 0)
                savings_rate = summary.get("summary", {}).get("savingsRate", 0)
                print(f"   Income: ${income:.2f}")
                print(f"   Expense: ${expense:.2f}")
                print(f"   Savings: ${savings:.2f} ({savings_rate:.0%})")

    async def cmd_full_sync(self, args) -> None:
        """Handle full data synchronization."""
        await self.ensure_authenticated()

        cache_path = self.setup_cache(args.cache_dir)

        print("🔄 Starting full data synchronization...")

        # Get all data types
        data_operations = [
            ("subscription", self.mm.get_subscription_details()),
            ("accounts", self.mm.get_accounts()),
            ("institutions", self.mm.get_institutions()),
            ("budgets", self.mm.get_budgets()),
            ("transactions_summary", self.mm.get_transactions_summary()),
            ("categories", self.mm.get_transaction_categories()),
            ("transactions", self.mm.get_transactions(limit=args.transaction_limit)),
        ]

        # Add cashflow if dates provided
        if args.start_date and args.end_date:
            data_operations.append(
                ("cashflow", self.mm.get_cashflow(start_date=args.start_date, end_date=args.end_date))
            )

        # Execute all operations
        for name, operation in data_operations:
            try:
                print(f"📥 Fetching {name}...")
                data = await operation

                # Save to cache
                filename = f"{name}.json"
                indent = 4 if name == "budgets" else None
                self.save_json(data, cache_path / filename, indent=indent)

            except Exception as e:
                print(f"❌ Error fetching {name}: {e}")

        print(f"\n✅ Full sync completed! Data saved to: {cache_path}")
        print("Files created:")
        for file_path in cache_path.glob("*.json"):
            print(f"  - {file_path.name}")

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="MonarchMoney CLI - Access your financial data from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  monarchmoney login                    # Authenticate with Monarch Money
  monarchmoney status                   # Show account status
  monarchmoney accounts                 # List all accounts
  monarchmoney transactions -l 20       # Show 20 recent transactions
  monarchmoney budgets -o budgets.json  # Save budgets to file
  monarchmoney cashflow --start-date 2023-10-01 --end-date 2023-10-31
  monarchmoney sync                     # Full data synchronization
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Authenticate with Monarch Money")
    login_parser.add_argument("--force", action="store_true", help="Force fresh login")

    # Status command
    subparsers.add_parser("status", help="Show account status and subscription details")

    # Accounts command
    accounts_parser = subparsers.add_parser("accounts", help="List accounts")
    accounts_parser.add_argument("-o", "--output", help="Output file path (JSON)")

    # Transactions command
    transactions_parser = subparsers.add_parser("transactions", help="List transactions")
    transactions_parser.add_argument("-l", "--limit", type=int, default=10, help="Number of transactions to retrieve")
    transactions_parser.add_argument("-o", "--output", help="Output file path (JSON)")

    # Budgets command
    budgets_parser = subparsers.add_parser("budgets", help="Show budgets")
    budgets_parser.add_argument("-o", "--output", help="Output file path (JSON)")

    # Cashflow command
    cashflow_parser = subparsers.add_parser("cashflow", help="Show cashflow analysis")
    cashflow_parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    cashflow_parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    cashflow_parser.add_argument("-o", "--output", help="Output file path (JSON)")

    # Full sync command
    sync_parser = subparsers.add_parser("sync", help="Full data synchronization")
    sync_parser.add_argument("--cache-dir", help="Custom cache directory name")
    sync_parser.add_argument("--transaction-limit", type=int, default=100, help="Number of transactions to sync")
    sync_parser.add_argument("--start-date", help="Start date for cashflow (YYYY-MM-DD)")
    sync_parser.add_argument("--end-date", help="End date for cashflow (YYYY-MM-DD)")

    return parser

async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = MonarchMoneyCLI()

    try:
        # Route to appropriate command handler
        if args.command == "login":
            await cli.cmd_login(args)
        elif args.command == "status":
            await cli.cmd_status(args)
        elif args.command == "accounts":
            await cli.cmd_accounts(args)
        elif args.command == "transactions":
            await cli.cmd_transactions(args)
        elif args.command == "budgets":
            await cli.cmd_budgets(args)
        elif args.command == "cashflow":
            await cli.cmd_cashflow(args)
        elif args.command == "sync":
            await cli.cmd_full_sync(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\n⏸️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0

def cli_main():
    """Entry point for CLI script."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    cli_main()