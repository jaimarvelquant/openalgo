# External `openalgo` Library - Quick Reference

**TL;DR:** ✅ **KEEP IT** - It's a client SDK, not a conflict.

---

## What is it?

The `openalgo==1.0.32` package is a **Python client SDK** (like `requests` or `boto3`) that connects TO our MarvelQuant server.

```python
from openalgo import api

# This creates a CLIENT that connects to OUR server
client = api(
    api_key="your_key",
    host="http://127.0.0.1:5000"  # ← OUR MarvelQuant server
)

# Client makes HTTP requests to OUR server's API
client.placeorder(...)
```

---

## Why keep it?

1. **No conflict:** It's a client library (like `requests`), not part of our codebase
2. **Used everywhere:** 19 files depend on it (strategies, tests, MCP server, Telegram bot)
3. **Community-maintained:** We don't have to maintain it
4. **Stable:** Version 1.0.32 is proven and working

---

## Files using it

| Category | Count | Examples |
|----------|-------|----------|
| Strategy Examples | 8 | `strategies/ltp_example.py` |
| Tests | 4 | `test/test_broker.py` |
| MCP Server | 2 | `mcp/mcpserver.py` |
| Download Scripts | 2 | `download/ieod.py` |
| Telegram Bot | 3 | `services/telegram_bot_service.py` |
| **TOTAL** | **19** | |

---

## What NOT to do

❌ **DO NOT** remove `openalgo==1.0.32` from `requirements.txt`  
❌ **DO NOT** remove `openalgo==1.0.32` from `pyproject.toml`  
❌ **DO NOT** change `from openalgo import api` imports  
❌ **DO NOT** rename the external library

---

## What TO do

✅ **KEEP** `openalgo==1.0.32` in dependencies  
✅ **UPDATE** documentation to clarify it's a client SDK  
✅ **TEST** that it still works after rebranding  
✅ **MONITOR** for community updates (optional)

---

## Analogy

Think of it like this:

- **MarvelQuant** = Our web server (like Apache/Nginx)
- **openalgo** = Client library (like `curl` or `requests`)

Just like renaming Apache doesn't affect `curl`, rebranding to MarvelQuant doesn't affect the `openalgo` client SDK.

---

## Documentation Update Needed

Add to README.md:

```markdown
## Python Client SDK

Install the community-maintained client SDK:

\`\`\`bash
pip install openalgo
\`\`\`

The `openalgo` library is a Python client SDK for connecting to MarvelQuant servers:

\`\`\`python
from openalgo import api

client = api(
    api_key="your_api_key",
    host="http://127.0.0.1:5000"  # Your MarvelQuant server
)

# Place orders, get market data, manage positions
client.placeorder(symbol="RELIANCE", exchange="NSE", ...)
\`\`\`

For more information:
- GitHub: https://github.com/marketcalls/openalgo-python-library
- Documentation: https://docs.openalgo.in/trading-platform/python
```

---

## Testing After Rebranding

Run these to verify the client SDK still works:

```bash
# Test strategy examples
python strategies/ltp_example.py

# Test MCP server
python mcp/mcpserver.py YOUR_API_KEY http://127.0.0.1:5000

# Test Telegram bot
python services/telegram_bot_service.py

# Run integration tests
pytest test/test_broker.py
```

All should pass because the client SDK connects via HTTP/WebSocket, which doesn't change with rebranding.

---

## Questions?

**Q: Will rebranding break the external library?**  
A: ❌ No. It's a client that connects via HTTP. Server name doesn't matter.

**Q: Should we fork the library?**  
A: ❌ Not needed. Community version is stable and maintained.

**Q: Can we rename it to `marvelquant-sdk`?**  
A: ⚠️ Possible but not recommended. Would require 122-184 hours of work with no benefit.

**Q: What if the community stops maintaining it?**  
A: ⏰ Then we can fork or create our own. Not a concern now.

---

**Last Updated:** 2025-10-11  
**See Full Analysis:** `docs/bmad/DEPENDENCY_CONFLICT_ANALYSIS.md`

