# Playwright MCP for Auggie CLI

This guide helps you configure Playwright MCP (Model Context Protocol) server for browser automation with Auggie CLI.

## What is Playwright MCP?

Playwright MCP provides browser automation capabilities through the Model Context Protocol, allowing Auggie CLI to:
- Navigate web pages
- Interact with web elements (click, fill forms, etc.)
- Take screenshots
- Execute JavaScript
- Extract content from web pages

## Prerequisites

- Node.js 18+ (✅ v22.17.1 installed)
- Auggie CLI (✅ v0.5.8 installed)
- Playwright MCP server

## Installation

### 1. Install Playwright MCP Server

```bash
npm install -g @playwright/mcp
```

### 2. Create Auggie Configuration

Create the configuration directory and file:

```bash
mkdir -p ~/.auggie
```

Create `~/.auggie/config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "marvelquant": {
      "command": "/Users/maruth/projects/marvelquant/.venv/bin/python3",
      "args": [
        "/Users/maruth/projects/marvelquant/mcp/mcpserver.py",
        "75898c159b44ff462f6408b01991b520d522f56c82a255881d6f5b7da8264e8c",
        "http://127.0.0.1:5000"
      ]
    }
  }
}
```

### 3. Verify Installation

Test the Playwright MCP server:

```bash
npx @playwright/mcp@latest --help
```

Test with Auggie CLI:

```bash
auggie --mcp-config ~/.auggie/config.json "What MCP servers are available?" --print
```

## Usage Examples

### Basic Browser Automation

```bash
auggie --mcp-config ~/.auggie/config.json "Start a browser and navigate to https://example.com, then get the page title" --print
```

### Form Interaction

```bash
auggie --mcp-config ~/.auggie/config.json "Navigate to https://httpbin.org/forms/post, fill the 'custname' field with 'Test User', and take a screenshot" --print
```

### Web Scraping

```bash
auggie --mcp-config ~/.auggie/config.json "Go to https://news.ycombinator.com, extract all article titles, and save them to a file" --print
```

### Screenshot Capture

```bash
auggie --mcp-config ~/.auggie/config.json "Navigate to https://github.com, scroll down 500 pixels, and take a screenshot" --print
```

## Available Playwright Tools

### Browser Management
- `browser_navigate_playwright` - Navigate to URLs
- `browser_snapshot_playwright` - Take page snapshots
- `browser_click_playwright` - Click elements
- `browser_type_playwright` - Type text
- `browser_key_press_playwright` - Press keys

### Content Extraction
- `browser_get_text_playwright` - Extract text content
- `browser_get_attribute_playwright` - Get element attributes
- `browser_evaluate_playwright` - Execute JavaScript

### Advanced Operations
- `browser_screenshot_playwright` - Take screenshots
- `browser_scroll_playwright` - Scroll pages
- `browser_wait_for_playwright` - Wait for elements

## Configuration Options

### Playwright MCP Server Options

You can customize the Playwright MCP server with additional options:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--browser", "chrome",
        "--viewport-size", "1280x720"
      ]
    }
  }
}
```

### Available Options

- `--headless` - Run browser in headless mode
- `--browser <browser>` - Choose browser (chrome, firefox, webkit, msedge)
- `--viewport-size <size>` - Set viewport size (e.g., "1280x720")
- `--device <device>` - Emulate device (e.g., "iPhone 15")
- `--user-agent <ua>` - Set custom user agent
- `--timeout-action <ms>` - Action timeout (default: 5000ms)
- `--timeout-navigation <ms>` - Navigation timeout (default: 60000ms)

## Testing

Run the test script to verify functionality:

```bash
./test_auggie_mcp.sh
```

## Troubleshooting

### Common Issues

1. **MCP server not connecting**
   - Verify configuration file path is correct
   - Check that `@playwright/mcp` is installed globally
   - Ensure Node.js version is 18+

2. **Browser won't start**
   - Check if Playwright browsers are installed: `npx playwright install`
   - Verify system permissions for browser execution

3. **Permission errors**
   - Ensure Auggie CLI has proper permissions
   - Check file ownership and permissions

### Debug Mode

Enable debug output:

```bash
auggie --mcp-config ~/.auggie/config.json "your instruction" --print --verbose
```

## Security Considerations

- Playwright MCP runs locally and has access to your browser
- Be cautious when automating sensitive websites
- Consider using headless mode for production automation
- Monitor browser resource usage

## Integration with MarvelQuant

The configuration includes both Playwright and MarvelQuant MCP servers, enabling:

- **Browser Automation**: Web scraping, form filling, screenshots
- **Trading Operations**: Order placement, position management, market data

Example combined workflow:
```bash
auggie --mcp-config ~/.auggie/config.json "Navigate to a trading website, extract market data, and place an order using MarvelQuant" --print
```

## Support

For issues with:
- **Playwright MCP**: Check Playwright documentation
- **Auggie CLI**: Check Auggie CLI documentation
- **MCP Protocol**: Check Model Context Protocol specifications
- **Browser Automation**: See Playwright documentation

## Next Steps

1. Test basic browser automation
2. Explore web scraping capabilities
3. Integrate with MarvelQuant trading workflows
4. Build custom automation scripts
5. Set up automated testing workflows
