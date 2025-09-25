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

The main.py example includes intelligent session management with environment-based TTL (Time To Live):

### Development Mode (Default)
- **TTL**: 1 hour (60 minutes)
- **Valid sessions**: Sessions less than 1 hour old are reused
- **Expired sessions**: Sessions older than 1 hour are automatically cleared

### Production Mode
- **TTL**: 15 minutes (0.25 hours)
- **Valid sessions**: Sessions less than 15 minutes old are reused
- **Expired sessions**: Sessions older than 15 minutes are automatically cleared

### Environment Configuration
Set the `MONARCH_ENV` environment variable to control TTL:
```bash
# Development mode (1 hour TTL) - default
export MONARCH_ENV=development
python examples/main.py

# Production mode (15 minutes TTL)
export MONARCH_ENV=production
python examples/main.py
```

### Features
- **Automatic reuse**: Valid sessions are reused without prompting for login
- **Corrupted sessions**: Invalid session files are automatically cleared
- **Fresh login**: Only prompts for credentials when no valid session exists
- **Environment awareness**: Shows current mode in session status messages

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
