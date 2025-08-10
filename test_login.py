#!/usr/bin/env python3
"""
Test login functionality for MonarchMoney Python SDK.
"""

import asyncio
from monarchmoney import MonarchMoney

async def test_login():
    mm = MonarchMoney()
    await mm.interactive_login()

if __name__ == "__main__":
    asyncio.run(test_login())
