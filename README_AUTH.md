# Authentication Guide

This guide explains how to authenticate with the Monarch Money API using the Python SDK.

## Getting Your API Token

1. Log into [Monarch Money](https://app.monarchmoney.com)
2. Open Developer Tools (F12)
3. Go to Network tab
4. Look for any GraphQL request
5. Check the Request Headers for 'Authorization: Token YOUR_TOKEN_HERE'

## Using Your Token

### Environment Variable

The recommended way is to set your token as an environment variable:

```bash
export MONARCH_TOKEN='your_token_here'
```

Then the SDK will automatically use it:

```python
from monarchmoney import MonarchMoney

mm = MonarchMoney()  # Will use MONARCH_TOKEN from environment
```

### Direct Token Usage

You can also provide the token directly:

```python
from monarchmoney import MonarchMoney

mm = MonarchMoney(token='your_token_here')
```

### Session Management

The SDK can save and load authentication sessions:

```python
# Save session
mm.save_session('my_session.pickle')

# Load session
mm.load_session('my_session.pickle')

# Delete session
mm.delete_session('my_session.pickle')
```

## Security Best Practices

1. Never commit your token to version control
2. Use environment variables or secure credential storage
3. Rotate your token periodically
4. Keep your session files secure
5. Delete sessions when no longer needed

## Troubleshooting

Common authentication issues:

1. Token expired
   - Get a fresh token from the web app
   - Update your environment variable or session file

2. Network issues
   - Check your internet connection
   - Verify API endpoint accessibility

3. Permission issues
   - Ensure your token has the necessary permissions
   - Check if your account is active

4. Session issues
   - Try deleting and recreating your session file
   - Use a fresh token instead of a saved session
