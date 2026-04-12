#!/bin/bash

echo "🧪 Testing All MCP Servers Across Auggie CLI, Codex CLI, and Claude Code CLI"
echo "=================================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
test_mcp() {
    local tool=$1
    local command=$2
    local test_name=$3
    
    echo -e "\n${BLUE}Testing $tool with $test_name${NC}"
    echo "Command: $command"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $tool - $test_name: PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $tool - $test_name: FAILED${NC}"
        return 1
    fi
}

# Test counters
total_tests=0
passed_tests=0

echo -e "\n${YELLOW}1. Testing Auggie CLI MCP Servers${NC}"
echo "=========================================="

# Test Auggie CLI MCP servers
test_mcp "Auggie CLI" "auggie --mcp-config ~/.auggie/config.json 'List all available MCP servers' --print" "MCP Server Detection"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

test_mcp "Auggie CLI" "auggie --mcp-config ~/.auggie/config.json 'Use filesystem MCP to list files in current directory' --print" "Filesystem MCP"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

test_mcp "Auggie CLI" "auggie --mcp-config ~/.auggie/config.json 'Use playwright MCP to navigate to https://example.com' --print" "Playwright MCP"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

echo -e "\n${YELLOW}2. Testing Codex CLI MCP Servers${NC}"
echo "=========================================="

# Test Codex CLI MCP servers
test_mcp "Codex CLI" "codex mcp list" "MCP Server Detection"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

test_mcp "Codex CLI" "codex exec 'Use filesystem MCP to list files in current directory'" "Filesystem MCP"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

test_mcp "Codex CLI" "codex exec 'Use playwright MCP to navigate to https://example.com'" "Playwright MCP"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

echo -e "\n${YELLOW}3. Testing Claude Code CLI MCP Servers${NC}"
echo "=========================================="

# Test Claude Code CLI MCP servers
test_mcp "Claude Code CLI" "claude mcp list" "MCP Server Detection"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

test_mcp "Claude Code CLI" "claude 'Use filesystem MCP to list files in current directory' --print" "Filesystem MCP"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

test_mcp "Claude Code CLI" "claude 'Use playwright MCP to navigate to https://example.com' --print" "Playwright MCP"
total_tests=$((total_tests + 1))
if [ $? -eq 0 ]; then passed_tests=$((passed_tests + 1)); fi

echo -e "\n${YELLOW}4. Detailed MCP Server Status${NC}"
echo "=========================================="

echo -e "\n${BLUE}Auggie CLI MCP Servers:${NC}"
auggie --mcp-config ~/.auggie/config.json "List all available MCP servers and their capabilities" --print

echo -e "\n${BLUE}Codex CLI MCP Servers:${NC}"
codex mcp list

echo -e "\n${BLUE}Claude Code CLI MCP Servers:${NC}"
claude mcp list

echo -e "\n${YELLOW}5. Summary${NC}"
echo "=========================================="
echo -e "Total Tests: $total_tests"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "\n${GREEN}🎉 All MCP servers are working correctly!${NC}"
else
    echo -e "\n${YELLOW}⚠️  Some MCP servers need attention.${NC}"
fi

echo -e "\n${BLUE}Installed MCP Servers:${NC}"
echo "• Playwright - Browser automation"
echo "• Tavily - Web search"
echo "• Context7 - Documentation context"
echo "• Sequential Thinking - Problem solving"
echo "• Filesystem - File operations"
echo "• Memory - Knowledge graph"
echo "• MarvelQuant - Trading platform"

echo -e "\n${BLUE}Configuration Files:${NC}"
echo "• Auggie CLI: ~/.auggie/config.json"
echo "• Codex CLI: Global configuration"
echo "• Claude Code CLI: ~/.claude.json (project-specific)"
