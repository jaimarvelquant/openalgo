#!/usr/bin/env python3
"""
Standalone Playwright MCP Server
Can be run directly without installation
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

# Create MCP server
mcp = FastMCP("playwright")

# Global browser instance
browser: Optional[Browser] = None
context: Optional[BrowserContext] = None
page: Optional[Page] = None

@mcp.tool()
async def start_browser(headless: bool = True, browser_type: str = "chromium") -> str:
    """
    Start a browser instance.
    
    Args:
        headless: Whether to run browser in headless mode (default: True)
        browser_type: Browser type - 'chromium', 'firefox', or 'webkit' (default: 'chromium')
    """
    global browser, context, page
    
    try:
        playwright = await async_playwright().start()
        
        if browser_type.lower() == "firefox":
            browser = await playwright.firefox.launch(headless=headless)
        elif browser_type.lower() == "webkit":
            browser = await playwright.webkit.launch(headless=headless)
        else:
            browser = await playwright.chromium.launch(headless=headless)
        
        context = await browser.new_context()
        page = await context.new_page()
        
        return f"Browser started successfully ({browser_type}, headless={headless})"
    except Exception as e:
        return f"Error starting browser: {str(e)}"

@mcp.tool()
async def navigate_to_url(url: str) -> str:
    """
    Navigate to a specific URL.
    
    Args:
        url: The URL to navigate to
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        response = await page.goto(url)
        title = await page.title()
        return f"Navigated to {url}\nPage title: {title}\nStatus: {response.status if response else 'Unknown'}"
    except Exception as e:
        return f"Error navigating to {url}: {str(e)}"

@mcp.tool()
async def get_page_title() -> str:
    """Get the current page title."""
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        title = await page.title()
        return f"Page title: {title}"
    except Exception as e:
        return f"Error getting page title: {str(e)}"

@mcp.tool()
async def get_page_url() -> str:
    """Get the current page URL."""
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        url = page.url
        return f"Current URL: {url}"
    except Exception as e:
        return f"Error getting page URL: {str(e)}"

@mcp.tool()
async def click_element(selector: str) -> str:
    """
    Click an element on the page.
    
    Args:
        selector: CSS selector or text content to click
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        await page.click(selector)
        return f"Clicked element: {selector}"
    except Exception as e:
        return f"Error clicking element '{selector}': {str(e)}"

@mcp.tool()
async def fill_input(selector: str, text: str) -> str:
    """
    Fill an input field with text.
    
    Args:
        selector: CSS selector for the input field
        text: Text to fill in the field
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        await page.fill(selector, text)
        return f"Filled '{selector}' with: {text}"
    except Exception as e:
        return f"Error filling input '{selector}': {str(e)}"

@mcp.tool()
async def get_element_text(selector: str) -> str:
    """
    Get text content of an element.
    
    Args:
        selector: CSS selector for the element
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        text = await page.text_content(selector)
        return f"Text content of '{selector}': {text}"
    except Exception as e:
        return f"Error getting text from '{selector}': {str(e)}"

@mcp.tool()
async def get_element_attribute(selector: str, attribute: str) -> str:
    """
    Get an attribute value of an element.
    
    Args:
        selector: CSS selector for the element
        attribute: Attribute name to get
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        value = await page.get_attribute(selector, attribute)
        return f"Attribute '{attribute}' of '{selector}': {value}"
    except Exception as e:
        return f"Error getting attribute '{attribute}' from '{selector}': {str(e)}"

@mcp.tool()
async def wait_for_element(selector: str, timeout: int = 30000) -> str:
    """
    Wait for an element to appear on the page.
    
    Args:
        selector: CSS selector for the element
        timeout: Timeout in milliseconds (default: 30000)
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return f"Element '{selector}' found"
    except Exception as e:
        return f"Error waiting for element '{selector}': {str(e)}"

@mcp.tool()
async def take_screenshot(filename: Optional[str] = None) -> str:
    """
    Take a screenshot of the current page.
    
    Args:
        filename: Optional filename for the screenshot
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        if not filename:
            filename = f"screenshot_{int(asyncio.get_event_loop().time())}.png"
        
        await page.screenshot(path=filename)
        return f"Screenshot saved as: {filename}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

@mcp.tool()
async def get_page_content() -> str:
    """Get the full HTML content of the current page."""
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        content = await page.content()
        return f"Page content length: {len(content)} characters\nFirst 500 characters:\n{content[:500]}..."
    except Exception as e:
        return f"Error getting page content: {str(e)}"

@mcp.tool()
async def evaluate_javascript(script: str) -> str:
    """
    Execute JavaScript on the current page.
    
    Args:
        script: JavaScript code to execute
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        result = await page.evaluate(script)
        return f"JavaScript result: {result}"
    except Exception as e:
        return f"Error executing JavaScript: {str(e)}"

@mcp.tool()
async def scroll_page(direction: str = "down", pixels: int = 500) -> str:
    """
    Scroll the page.
    
    Args:
        direction: Scroll direction - 'down', 'up', 'left', 'right' (default: 'down')
        pixels: Number of pixels to scroll (default: 500)
    """
    global page
    
    if not page:
        return "Error: Browser not started. Call start_browser first."
    
    try:
        if direction.lower() == "up":
            await page.evaluate(f"window.scrollBy(0, -{pixels})")
        elif direction.lower() == "down":
            await page.evaluate(f"window.scrollBy(0, {pixels})")
        elif direction.lower() == "left":
            await page.evaluate(f"window.scrollBy(-{pixels}, 0)")
        elif direction.lower() == "right":
            await page.evaluate(f"window.scrollBy({pixels}, 0)")
        else:
            return f"Invalid direction '{direction}'. Use 'up', 'down', 'left', or 'right'"
        
        return f"Scrolled {direction} by {pixels} pixels"
    except Exception as e:
        return f"Error scrolling page: {str(e)}"

@mcp.tool()
async def close_browser() -> str:
    """Close the browser and clean up resources."""
    global browser, context, page
    
    try:
        if page:
            await page.close()
            page = None
        if context:
            await context.close()
            context = None
        if browser:
            await browser.close()
            browser = None
        
        return "Browser closed successfully"
    except Exception as e:
        return f"Error closing browser: {str(e)}"

@mcp.tool()
async def get_browser_status() -> str:
    """Get the current browser status."""
    global browser, context, page
    
    status = {
        "browser": "Running" if browser else "Not started",
        "context": "Active" if context else "Not created",
        "page": "Active" if page else "Not created",
        "current_url": page.url if page else "N/A"
    }
    
    return json.dumps(status, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio')
