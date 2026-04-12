#!/bin/bash

# Test script for Auggie CLI with Playwright MCP
echo "🧪 Testing Auggie CLI with Playwright MCP..."

# Test 1: Check available MCP servers
echo "Test 1: Checking available MCP servers..."
auggie --mcp-config ~/.auggie/config.json "What MCP servers are available?" --print --quiet

echo -e "\n" 

# Test 2: Basic browser automation
echo "Test 2: Basic browser automation..."
auggie --mcp-config ~/.auggie/config.json "Start a browser, navigate to https://httpbin.org/get, and get the page title" --print --quiet

echo -e "\n"

# Test 3: Form interaction
echo "Test 3: Form interaction..."
auggie --mcp-config ~/.auggie/config.json "Navigate to https://httpbin.org/forms/post, fill the 'custname' field with 'Test User', and take a screenshot" --print --quiet

echo -e "\n✅ All tests completed!"
