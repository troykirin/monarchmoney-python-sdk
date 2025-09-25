# MonarchMoney Python SDK Examples

This directory contains example scripts demonstrating how to use the MonarchMoney Python SDK.

## Examples

### `main.py`
Basic usage example showing how to:
- Perform interactive login
- Fetch and display accounts
- Handle authentication errors

### `get_accounts_with_token.py`
Token-based authentication example showing how to:
- Use API tokens for authentication
- Retrieve account information
- Handle token-based requests

## Setup

1. Install the SDK: `pip install -e .`
2. Configure your environment variables in `.envrc`
3. Run examples: `python examples/main.py`

## Automatic Session Management

The main.py example includes intelligent session management with a 1-hour TTL (Time To Live):

- **Valid sessions**: If a session file exists and is less than 1 hour old, it will be reused
- **Expired sessions**: Sessions older than 1 hour are automatically cleared and require fresh login
- **Corrupted sessions**: Invalid session files are automatically cleared
- **Fresh login**: Only prompts for credentials when no valid session exists

### Manual Session Management

If you need to manually manage sessions:

1. **Clear session and login fresh**: `python examples/clear_session_and_login.py`
2. **Or manually remove session**: `rm -rf .mm/` then run `python examples/main.py`

## Environment Variables

Make sure to set these in your `.envrc` file:
- `MONARCH_TOKEN`: Your Monarch Money API token
- `MONARCH_EMAIL`: Your Monarch Money email
- `MONARCH_PASSWORD`: Your Monarch Money password
- `MONARCH_MFA_SECRET`: Your MFA secret (if using 2FA)
