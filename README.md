# MonarchMoney Python SDK

A Python library for interacting with the Monarch Money API.

## Features

- Token-based authentication
- Account management
- Transaction tracking
- Apple financial account integration
- Command-line interface

## Installation

```bash
pip install monarchmoney
```

## Quick Start

```python
import asyncio
from monarchmoney import MonarchMoney

async def main():
    # Initialize with token
    mm = MonarchMoney(token='your_token_here')

    # Get accounts
    accounts = await mm.get_accounts()

    # Get recent transactions
    transactions = await mm.get_transactions(limit=5)

if __name__ == "__main__":
    asyncio.run(main())
```

## Authentication

You can authenticate using your Monarch Money API token:

1. Log into [Monarch Money](https://app.monarchmoney.com)
2. Open Developer Tools (F12)
3. Go to Network tab
4. Look for any GraphQL request
5. Check the Request Headers for 'Authorization: Token YOUR_TOKEN_HERE'

Then use the token:

```python
mm = MonarchMoney(token='your_token_here')
```

Or set it as an environment variable:

```bash
export MONARCH_TOKEN='your_token_here'
```

## Command Line Interface

The package includes a command-line interface:

```bash
# Get accounts
python monarch_cli.py accounts

# Get recent transactions
python monarch_cli.py transactions --limit 10
```

## Apple Account Integration

Special tools for managing Apple financial accounts:

```bash
# Analyze Apple accounts
python analyze_apple_accounts.py

# Analyze Apple transactions
python analyze_apple_transactions.py

# Migrate Apple Cash transactions
python migrate_apple_cash_transactions.py input_file.json
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest tests/test_monarchmoney.py

# Run single test
python -m unittest tests.test_monarchmoney.TestMonarchMoney.test_get_accounts

# Format code
black monarchmoney/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
