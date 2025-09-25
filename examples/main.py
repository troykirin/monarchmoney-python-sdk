import asyncio
import os
import json
from pathlib import Path
from datetime import datetime

from monarchmoney import MonarchMoney

_SESSION_FILE_ = ".mm/mm_session.pickle"
_CACHE_DIR_ = "cache"


def clear_session():
    """Remove existing session file if it exists."""
    session_path = Path(_SESSION_FILE_)
    if session_path.exists():
        print(f"🗑️  Clearing existing session file: {_SESSION_FILE_}")
        session_path.unlink()
        print("✅ Session cleared")
    else:
        print("ℹ️  No existing session file found")


def setup_cache():
    """Create cache directory with timestamp subdirectory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_path = Path(_CACHE_DIR_) / timestamp
    cache_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created cache directory: {cache_path}")
    return cache_path


def main() -> None:
    # Clear any existing session for fresh start
    clear_session()
    
    # Setup cache directory
    cache_path = setup_cache()
    
    # Use session file
    mm = MonarchMoney(session_file=_SESSION_FILE_)
    
    # Perform fresh interactive login
    print("🔐 Starting fresh login...")
    asyncio.run(mm.interactive_login(use_saved_session=False, save_session=True))
    print("✅ Login successful!")

    # Subscription details
    subs = asyncio.run(mm.get_subscription_details())
    print(subs)

    # Accounts
    accounts = asyncio.run(mm.get_accounts())
    with open(cache_path / "accounts.json", "w") as outfile:
        json.dump(accounts, outfile)

    # Institutions
    institutions = asyncio.run(mm.get_institutions())
    with open(cache_path / "institutions.json", "w") as outfile:
        json.dump(institutions, outfile)

    # Budgets
    budgets = asyncio.run(mm.get_budgets())
    with open(cache_path / "budgets.json", "w") as outfile:
        json.dump(budgets, outfile, indent=4)

    # Transactions summary
    transactions_summary = asyncio.run(mm.get_transactions_summary())
    with open(cache_path / "transactions_summary.json", "w") as outfile:
        json.dump(transactions_summary, outfile)

    # Transaction categories
    categories = asyncio.run(mm.get_transaction_categories())
    with open(cache_path / "categories.json", "w") as outfile:
        json.dump(categories, outfile)

    income_categories = dict()
    for c in categories.get("categories"):
        if c.get("group").get("type") == "income":
            print(
                f'{c.get("group").get("type")} - {c.get("group").get("name")} - {c.get("name")}'
            )
            income_categories[c.get("name")] = 0

    expense_category_groups = dict()
    for c in categories.get("categories"):
        if c.get("group").get("type") == "expense":
            print(
                f'{c.get("group").get("type")} - {c.get("group").get("name")} - {c.get("name")}'
            )
            expense_category_groups[c.get("group").get("name")] = 0

    # Transactions
    transactions = asyncio.run(mm.get_transactions(limit=10))
    with open(cache_path / "transactions.json", "w") as outfile:
        json.dump(transactions, outfile)

    # Cashflow
    cashflow = asyncio.run(
        mm.get_cashflow(start_date="2023-10-01", end_date="2023-10-31")
    )
    with open(cache_path / "cashflow.json", "w") as outfile:
        json.dump(cashflow, outfile)

    for c in cashflow.get("summary"):
        print(
            f'Income: {c.get("summary").get("sumIncome")} '
            f'Expense: {c.get("summary").get("sumExpense")} '
            f'Savings: {c.get("summary").get("savings")} '
            f'({c.get("summary").get("savingsRate"):.0%})'
        )

    for c in cashflow.get("byCategory"):
        if c.get("groupBy").get("category").get("group").get("type") == "income":
            income_categories[c.get("groupBy").get("category").get("name")] += c.get(
                "summary"
            ).get("sum")

    print()
    for c in cashflow.get("byCategoryGroup"):
        if c.get("groupBy").get("categoryGroup").get("type") == "expense":
            expense_category_groups[
                c.get("groupBy").get("categoryGroup").get("name")
            ] += c.get("summary").get("sum")

    print(income_categories)
    print()
    print(expense_category_groups)
    
    print(f"\n📁 All data files saved to: {cache_path}")
    print("Files created:")
    for file_path in cache_path.glob("*.json"):
        print(f"  - {file_path.name}")


main()
