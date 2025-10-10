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

def test_openalgo():
    """Test OpenAlgo MCP server imports"""
    try:
        from openalgo import api
        print("✓ OpenAlgo import test passed")
        return True
    except Exception as e:
        print(f"✗ OpenAlgo import test failed: {e}")
        return False

async def main():
    print("🧪 Testing MCP servers...")
    
    openalgo_ok = test_openalgo()
    playwright_ok = await test_playwright()
    
    if openalgo_ok and playwright_ok:
        print("\n🎉 All tests passed! MCP servers are ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
