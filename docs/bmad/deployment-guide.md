# Jainam Prop Broker - Deployment Guide

**Version:** 1.0
**Last Updated:** 2025-10-07
**Target:** OpenAlgo Jainam Prop Integration

---

## Overview

This guide covers the deployment and configuration of the Jainam Prop broker integration for OpenAlgo. Follow these steps carefully to ensure secure and proper setup.

---

## Prerequisites

Before deploying, ensure you have:

1. **Jainam Prop Account** with API access enabled
2. **API Credentials** from Jainam (4 required credentials):
   - Interactive API Key
   - Interactive API Secret
   - Market Data API Key
   - Market Data API Secret
3. **OpenAlgo Platform** installed and running
4. **Python 3.8+** environment

---

## Step 1: Obtain Jainam API Credentials

### 1.1 Register for API Access

1. Visit the Jainam Prop trading platform: http://smpb.jainam.in:4143
2. Log in to your account
3. Navigate to API settings or contact Jainam support to enable API access
4. Request both **Interactive API** and **Market Data API** credentials

### 1.2 Verify You Have All 4 Credentials

You should receive:
- ✅ Interactive API Key (alphanumeric, ~20-30 characters)
- ✅ Interactive API Secret (alphanumeric, ~10-20 characters)
- ✅ Market Data API Key (alphanumeric, ~20-30 characters)
- ✅ Market Data API Secret (alphanumeric, ~10-20 characters)

**Security Note:** Keep these credentials confidential. Never share them or commit them to version control.

---

## Step 2: Configure Environment Variables

### 2.1 Locate Configuration File

OpenAlgo uses a `.env` file in the project root directory for configuration.

```bash
cd /path/to/openalgo
ls -la .env
```

### 2.2 Add Jainam Credentials

Open the `.env` file in your preferred text editor:

```bash
nano .env
# or
vim .env
```

### 2.3 Add or Update the Following Variables

Add these lines to your `.env` file (replace placeholders with your actual credentials):

```bash
# =============================================================================
# Jainam Prop Broker Configuration
# =============================================================================

# Interactive API Credentials (for order placement and portfolio management)
JAINAM_INTERACTIVE_API_KEY='your_actual_interactive_api_key_here'
JAINAM_INTERACTIVE_API_SECRET='your_actual_interactive_secret_here'

# Market Data API Credentials (for real-time market data and quotes)
JAINAM_MARKET_API_KEY='your_actual_market_data_api_key_here'
JAINAM_MARKET_API_SECRET='your_actual_market_data_secret_here'

# Callback URL for OAuth authentication (adjust if using different host/port)
REDIRECT_URL='http://127.0.0.1:5000/jainam_prop/callback'
```

### 2.4 Example Configuration

```bash
# Example (DO NOT use these values - they are for illustration only)
JAINAM_INTERACTIVE_API_KEY='abc123def456ghi789jkl012'
JAINAM_INTERACTIVE_API_SECRET='Xyz987$wv'
JAINAM_MARKET_API_KEY='mno345pqr678stu901vwx234'
JAINAM_MARKET_API_SECRET='Pqr654@Ab'
REDIRECT_URL='http://127.0.0.1:5000/jainam_prop/callback'
```

### 2.5 Save and Verify

1. Save the `.env` file
2. Verify the file is not accessible by other users:

```bash
chmod 600 .env
```

3. Ensure `.env` is in your `.gitignore`:

```bash
echo ".env" >> .gitignore
```

---

## Step 3: Verify Broker Configuration

### 3.1 Check Valid Brokers List

Ensure `jainam_prop` is included in the `VALID_BROKERS` variable in your `.env` file:

```bash
VALID_BROKERS='...,jainam_prop,...'
```

### 3.2 Test Credential Loading

You can test if credentials are loaded correctly by running a Python check:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Check all 4 credentials
interactive_key = os.getenv('JAINAM_INTERACTIVE_API_KEY')
interactive_secret = os.getenv('JAINAM_INTERACTIVE_API_SECRET')
market_key = os.getenv('JAINAM_MARKET_API_KEY')
market_secret = os.getenv('JAINAM_MARKET_API_SECRET')

if all([interactive_key, interactive_secret, market_key, market_secret]):
    print("✅ All Jainam credentials loaded successfully")
else:
    print("❌ Missing credentials:")
    if not interactive_key: print("  - JAINAM_INTERACTIVE_API_KEY")
    if not interactive_secret: print("  - JAINAM_INTERACTIVE_API_SECRET")
    if not market_key: print("  - JAINAM_MARKET_API_KEY")
    if not market_secret: print("  - JAINAM_MARKET_API_SECRET")
```

---

## Step 4: Download Master Contract

The master contract contains symbol-to-token mappings required for trading.

### 4.1 Via OpenAlgo Admin UI

1. Start the OpenAlgo application
2. Log in to the admin interface
3. Navigate to: **Settings → Broker Configuration → Jainam Prop**
4. Click **"Download Master Contract"**
5. Wait for completion (may take 30-60 seconds)

### 4.2 Via API Endpoint (Alternative)

```bash
curl -X POST http://127.0.0.1:5000/api/v1/master_contract \
  -H "Content-Type: application/json" \
  -d '{"broker": "jainam_prop"}'
```

### 4.3 Verify Master Contract Downloaded

Check the database for Jainam symbols:

```bash
sqlite3 db/openalgo.db "SELECT COUNT(*) FROM symbol_token WHERE broker='jainam_prop';"
```

Expected output: A number greater than 100,000 (indicating successful download)

---

## Step 5: Restart Application

### 5.1 Stop the Application

If running as a service:
```bash
sudo systemctl stop openalgo
```

If running in development mode:
```bash
# Press Ctrl+C in the terminal where Flask is running
```

### 5.2 Start the Application

Production mode (with Gunicorn):
```bash
sudo systemctl start openalgo
```

Development mode:
```bash
python app.py
```

### 5.3 Verify Application Started

Check application logs for successful startup:

```bash
# For systemd service
sudo journalctl -u openalgo -f

# For development mode
# Check terminal output for:
# "Running on http://127.0.0.1:5000"
```

---

## Step 6: Test Authentication

### 6.1 Initiate Broker Login

1. Navigate to: http://127.0.0.1:5000
2. Go to **Broker Login** section
3. Select **Jainam Prop** from the broker dropdown
4. Click **"Login"**

### 6.2 Complete OAuth Flow

1. You'll be redirected to Jainam's authentication page
2. Enter your Jainam trading credentials (username/password)
3. Approve the API access request
4. You'll be redirected back to OpenAlgo

### 6.3 Verify Successful Authentication

Check for success message:
- ✅ "Successfully authenticated with Jainam Prop"
- ✅ Your Jainam account details displayed

---

## Step 7: Verify Broker Functionality

### 7.1 Test Quote Fetching

```bash
curl -X POST http://127.0.0.1:5000/api/v1/quotes \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE-EQ",
    "exchange": "NSE"
  }'
```

Expected response: Live quote data for RELIANCE stock

### 7.2 Test Order Placement (Optional - Paper Trading Recommended)

**⚠️ WARNING: This will place a real order! Use small quantities for testing.**

```bash
curl -X POST http://127.0.0.1:5000/api/v1/placeorder \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "SBIN-EQ",
    "exchange": "NSE",
    "action": "BUY",
    "quantity": 1,
    "pricetype": "MARKET",
    "product": "MIS"
  }'
```

---

## Troubleshooting

### Issue 1: "Missing Credentials" Error

**Symptom:**
```
ValueError: JAINAM_INTERACTIVE_API_KEY environment variable is not set
```

**Solution:**
1. Verify `.env` file contains all 4 Jainam credentials
2. Check for typos in variable names
3. Ensure no extra spaces around `=` sign
4. Restart the application after updating `.env`

---

### Issue 2: Authentication Fails

**Symptom:**
```
API error: Invalid credentials
```

**Solutions:**
1. Verify credentials are correct (copy-paste directly from Jainam)
2. Check if API access is enabled for your account
3. Contact Jainam support to verify API status
4. Ensure credentials haven't expired or been revoked

---

### Issue 3: Master Contract Download Fails

**Symptom:**
```
Error downloading master contract: Connection timeout
```

**Solutions:**
1. Check internet connectivity
2. Verify Jainam API is accessible: `curl http://smpb.jainam.in:4143`
3. Check firewall settings
4. Try downloading again (may be temporary API issue)
5. Verify Market Data API credentials are correct

---

### Issue 4: "Symbol Not Found" Error During Order Placement

**Symptom:**
```
Symbol SBIN-EQ not found for exchange NSE
```

**Solutions:**
1. Verify master contract was downloaded successfully
2. Re-download master contract (may be outdated)
3. Check symbol format (should be `SYMBOL-EQ` for equity)
4. Verify exchange is correct (`NSE`, `BSE`, etc.)

---

## Security Best Practices

### 1. Credential Management

✅ **DO:**
- Store credentials in `.env` file only
- Use different credentials for production and testing (if available)
- Rotate credentials periodically (every 90 days recommended)
- Keep `.env` file permissions restricted: `chmod 600 .env`
- Add `.env` to `.gitignore`

❌ **DON'T:**
- Commit credentials to version control
- Share credentials via email or messaging apps
- Store credentials in application code
- Use production credentials in development environment
- Log or display credentials in error messages

### 2. Access Control

- Limit access to the server where OpenAlgo is deployed
- Use SSH keys instead of passwords for server access
- Enable firewall rules to restrict API access
- Monitor API access logs for suspicious activity

### 3. Monitoring

- Set up alerts for failed authentication attempts
- Monitor API usage for unusual patterns
- Review audit logs regularly
- Track credential usage and expiry dates

---

## Rollback Procedure

If you need to rollback the deployment:

### 1. Restore Previous `.env` File

```bash
cp .env.backup .env
```

### 2. Restart Application

```bash
sudo systemctl restart openalgo
```

### 3. Verify Rollback Successful

Check application logs and test basic functionality.

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review authentication logs
- Check for API errors in logs
- Verify master contract is up-to-date

**Monthly:**
- Re-download master contract
- Review and update credentials if needed
- Test authentication flow

**Quarterly:**
- Rotate API credentials (if supported by Jainam)
- Review security audit logs
- Update deployment documentation

---

## Support

### Getting Help

1. **OpenAlgo Documentation:** https://docs.openalgo.in/
2. **Jainam Support:** Contact via http://smpb.jainam.in:4143
3. **GitHub Issues:** https://github.com/marketcalls/openalgo/issues

### Reporting Issues

When reporting issues, include:
- OpenAlgo version
- Python version
- Error messages (WITHOUT credentials)
- Steps to reproduce
- Expected vs actual behavior

---

## Appendix

### A. Environment Variable Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `JAINAM_INTERACTIVE_API_KEY` | Yes | Interactive API Key for order placement | `abc123def456...` |
| `JAINAM_INTERACTIVE_API_SECRET` | Yes | Interactive API Secret | `Xyz987$wv` |
| `JAINAM_MARKET_API_KEY` | Yes | Market Data API Key for quotes | `mno345pqr678...` |
| `JAINAM_MARKET_API_SECRET` | Yes | Market Data API Secret | `Pqr654@Ab` |
| `REDIRECT_URL` | Yes | OAuth callback URL | `http://127.0.0.1:5000/jainam_prop/callback` |

### B. API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/placeorder` | POST | Place a new order |
| `/api/v1/quotes` | POST | Get live quotes |
| `/api/v1/orderbook` | GET | Get order history |
| `/api/v1/positions` | GET | Get current positions |
| `/api/v1/holdings` | GET | Get holdings |
| `/api/v1/master_contract` | POST | Download master contract |

### C. Common Symbol Formats

| Exchange | Symbol Format | Example |
|----------|---------------|---------|
| NSE Equity | `SYMBOL-EQ` | `RELIANCE-EQ` |
| BSE Equity | `SYMBOL-EQ` | `SBIN-EQ` |
| NFO Futures | `SYMBOLYYMONFUT` | `NIFTY24DECFUT` |
| NFO Options | `SYMBOLYYMONCE` | `NIFTY24DEC20000CE` |

---

**Document Version:** 1.0
**Author:** OpenAlgo Development Team
**License:** AGPL v3.0
