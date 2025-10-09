#!/bin/bash

# Global MCP Setup Script for Codex and Claude (Non-interactive)
# This script configures Playwright MCP globally for both applications

set -e

echo "🚀 Setting up Global Playwright MCP for Codex and Claude..."

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
PLAYWRIGHT_SERVER="$PROJECT_DIR/mcp/playwright_mcp_standalone.py"

print_info "Project directory: $PROJECT_DIR"

# Check if Playwright MCP server exists
if [ ! -f "$PLAYWRIGHT_SERVER" ]; then
    print_error "Playwright MCP server not found at $PLAYWRIGHT_SERVER"
    exit 1
fi

# Check if playwright is installed globally
if ! command -v playwright &> /dev/null; then
    print_error "Playwright not found globally. Installing..."
    pipx install playwright
fi

# Check if mcp is installed globally
if ! command -v mcp &> /dev/null; then
    print_error "MCP not found globally. Installing..."
    pipx install mcp
fi

print_status "Global dependencies found"

# Install Playwright browsers globally
print_info "Installing Playwright browsers globally..."
playwright install

print_status "Playwright browsers installed globally"

# Create configuration files
print_info "Creating global MCP configuration files..."

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

# Create Codex configuration (Playwright only)
cat > "$CODEX_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "playwright": {
      "command": "python3",
      "args": [
        "$PLAYWRIGHT_SERVER"
      ]
    }
  }
}
EOF

# Create Claude configuration (Playwright only)
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "playwright": {
      "command": "python3",
      "args": [
        "$PLAYWRIGHT_SERVER"
      ]
    }
  }
}
EOF

print_status "Configuration files created"

# Test Playwright MCP server
print_info "Testing Playwright MCP server..."

# Create a simple test
cat > "$PROJECT_DIR/mcp/test_global_playwright.py" << 'EOF'
#!/usr/bin/env python3
"""
Test script for global Playwright MCP server
"""

import asyncio
import sys
import os

async def test_playwright():
    """Test Playwright functionality"""
    try:
        from playwright.async_api import async_playwright
        
        print("Testing global Playwright...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://example.com")
        title = await page.title()
        print(f"✓ Global Playwright test passed - Page title: {title}")
        
        await browser.close()
        await playwright.stop()
        return True
    except Exception as e:
        print(f"✗ Global Playwright test failed: {e}")
        return False

async def main():
    print("🧪 Testing global Playwright MCP...")
    
    playwright_ok = await test_playwright()
    
    if playwright_ok:
        print("\n🎉 Global Playwright MCP is ready!")
    else:
        print("\n⚠️  Global Playwright test failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x "$PROJECT_DIR/mcp/test_global_playwright.py"

# Run the test
print_info "Running global Playwright test..."
if python3 "$PROJECT_DIR/mcp/test_global_playwright.py"; then
    print_status "Global Playwright test passed!"
else
    print_warning "Global Playwright test failed - check the output above"
fi

echo
print_status "Global MCP setup completed!"
echo
print_info "Configuration files created:"
print_info "  Codex: $CODEX_CONFIG_FILE"
print_info "  Claude: $CLAUDE_CONFIG_FILE"
echo
print_info "Available MCP servers:"
print_info "  - playwright: Browser automation capabilities (GLOBAL)"
echo
print_warning "Next steps:"
print_warning "  1. Restart Codex/Cursor and Claude Desktop"
print_warning "  2. Verify MCP servers are connected in the applications"
print_warning "  3. Test functionality by asking AI to use browser automation tools"
echo
print_info "Test the setup by running: python3 $PROJECT_DIR/mcp/test_global_playwright.py"
echo
print_info "Global Playwright MCP is now available system-wide!"
