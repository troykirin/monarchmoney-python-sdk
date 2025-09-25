# Quick Reference Guide

Common operations with the MonarchMoney Python SDK.

## Accounts

```python
# Get all accounts
accounts = await mm.get_accounts()

# Get account balances
total_assets = 0
total_liabilities = 0

for account in accounts.get('accounts', []):
    balance = account.get('currentBalance', 0)
    is_asset = account.get('isAsset', True)

    if is_asset:
        total_assets += balance
    else:
        total_liabilities += abs(balance)

net_worth = total_assets - total_liabilities
```

## Transactions

```python
# Get recent transactions
transactions = await mm.get_transactions(limit=5)

# Get transactions by date range
from datetime import datetime, timedelta

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

transactions = await mm.get_transactions(
    start_date=start_date,
    end_date=end_date
)

# Get transactions by account
transactions = await mm.get_transactions(
    account_ids=['account_id_here']
)

# Get transactions by category
transactions = await mm.get_transactions(
    category_ids=['category_id_here']
)

# Search transactions
transactions = await mm.get_transactions(
    search="grocery"
)
```

## Apple Account Management

```python
# Analyze Apple accounts
from analyze_apple_accounts import analyze_apple_accounts
await analyze_apple_accounts()

# Analyze Apple transactions
from analyze_apple_transactions import analyze_apple_transactions
await analyze_apple_transactions(days=30)

# Migrate Apple Cash transactions
from migrate_apple_cash_transactions import migrate_apple_cash_transactions
await migrate_apple_cash_transactions('transactions.json')
```

## Command Line

```bash
# Get accounts
python monarch_cli.py accounts

# Get transactions
python monarch_cli.py transactions --limit 10

# Get accounts with token
python get_accounts_with_token.py

# Test login
python test_login.py
```

## Environment Variables

```bash
# Set API token
export MONARCH_TOKEN='your_token_here'

# Check token
echo $MONARCH_TOKEN
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest tests/test_monarchmoney.py

# Format code
black monarchmoney/ tests/
```
