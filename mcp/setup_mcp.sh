#!/bin/bash

# MCP Setup Script for Codex and Claude
# This script helps configure Model Context Protocol servers

set -e

echo "🚀 Setting up MCP for Codex and Claude..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python3"
OPENALGO_SERVER="$PROJECT_DIR/mcp/mcpserver.py"
PLAYWRIGHT_SERVER="$PROJECT_DIR/mcp/playwright_mcp_server.py"

print_info "Project directory: $PROJECT_DIR"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    print_error "Virtual environment not found at $VENV_PYTHON"
    print_info "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if MCP servers exist
if [ ! -f "$OPENALGO_SERVER" ]; then
    print_error "MarvelQuant MCP server not found at $OPENALGO_SERVER"
    exit 1
fi

if [ ! -f "$PLAYWRIGHT_SERVER" ]; then
    print_error "Playwright MCP server not found at $PLAYWRIGHT_SERVER"
    exit 1
fi

print_status "Virtual environment and MCP servers found"

# Get API key from user
echo
print_info "Please enter your MarvelQuant API key:"
read -s API_KEY

if [ -z "$API_KEY" ]; then
    print_error "API key is required"
    exit 1
fi

# Create configuration files
print_info "Creating MCP configuration files..."

# Codex configuration
CODEX_CONFIG_DIR="$HOME/Library/Application Support/Cursor/User"
CODEX_CONFIG_FILE="$CODEX_CONFIG_DIR/settings.json"

# Claude configuration
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Create directories if they don't exist
mkdir -p "$CODEX_CONFIG_DIR"
mkdir -p "$CLAUDE_CONFIG_DIR"

# Backup existing configs
if [ -f "$CODEX_CONFIG_FILE" ]; then
    cp "$CODEX_CONFIG_FILE" "$CODEX_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    print_warning "Backed up existing Codex config"
fi

if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    print_warning "Backed up existing Claude config"
fi

# Create Codex configuration
cat > "$CODEX_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "marvelquant": {
      "command": "$VENV_PYTHON",
      "args": [
        "$OPENALGO_SERVER",
        "$API_KEY",
        "http://127.0.0.1:5000"
      ]
    },
    "playwright": {
      "command": "$VENV_PYTHON",
      "args": [
        "$PLAYWRIGHT_SERVER"
      ]
    }
  }
}
EOF

# Create Claude configuration
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "marvelquant": {
      "command": "$VENV_PYTHON",
      "args": [
        "$OPENALGO_SERVER",
        "$API_KEY",
        "http://127.0.0.1:5000"
      ]
    },
    "playwright": {
      "command": "$VENV_PYTHON",
      "args": [
        "$PLAYWRIGHT_SERVER"
      ]
    }
  }
}
EOF

print_status "Configuration files created"

# Test MCP servers
print_info "Testing MCP servers..."

# Test MarvelQuant server
if $VENV_PYTHON "$OPENALGO_SERVER" --help > /dev/null 2>&1; then
    print_status "MarvelQuant MCP server test passed"
else
    print_warning "MarvelQuant MCP server test failed - this is normal for MCP servers"
fi

# Test Playwright server
if $VENV_PYTHON "$PLAYWRIGHT_SERVER" --help > /dev/null 2>&1; then
    print_status "Playwright MCP server test passed"
else
    print_warning "Playwright MCP server test failed - this is normal for MCP servers"
fi

# Create a test script
cat > "$PROJECT_DIR/mcp/test_mcp.py" << 'EOF'
#!/usr/bin/env python3
"""
Test script for MCP servers
"""

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_playwright():
    """Test Playwright MCP server functionality"""
    try:
        from playwright.async_api import async_playwright
        
        print("Testing Playwright...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://example.com")
        title = await page.title()
        print(f"✓ Playwright test passed - Page title: {title}")
        
        await browser.close()
        await playwright.stop()
        return True
    except Exception as e:
        print(f"✗ Playwright test failed: {e}")
        return False

def test_marvelquant():
    """Test MarvelQuant MCP server imports"""
    try:
        from marvelquant import api
        print("✓ MarvelQuant import test passed")
        return True
    except Exception as e:
        print(f"✗ MarvelQuant import test failed: {e}")
        return False

async def main():
    print("🧪 Testing MCP servers...")
    
    marvelquant_ok = test_marvelquant()
    playwright_ok = await test_playwright()
    
    if marvelquant_ok and playwright_ok:
        print("\n🎉 All tests passed! MCP servers are ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x "$PROJECT_DIR/mcp/test_mcp.py"

print_status "Test script created at $PROJECT_DIR/mcp/test_mcp.py"

# Run the test
print_info "Running MCP server tests..."
if $VENV_PYTHON "$PROJECT_DIR/mcp/test_mcp.py"; then
    print_status "All tests passed!"
else
    print_warning "Some tests failed - check the output above"
fi

echo
print_status "MCP setup completed!"
echo
print_info "Configuration files created:"
print_info "  Codex: $CODEX_CONFIG_FILE"
print_info "  Claude: $CLAUDE_CONFIG_FILE"
echo
print_info "Available MCP servers:"
print_info "  - marvelquant: Trading and market data functionality"
print_info "  - playwright: Browser automation capabilities"
echo
print_warning "Next steps:"
print_warning "  1. Restart Codex/Cursor and Claude Desktop"
print_warning "  2. Verify MCP servers are connected in the applications"
print_warning "  3. Test functionality by asking AI to use the tools"
echo
print_info "Test the setup by running: $VENV_PYTHON $PROJECT_DIR/mcp/test_mcp.py"
