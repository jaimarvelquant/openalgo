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
