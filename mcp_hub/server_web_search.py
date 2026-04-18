"""🔍 MCP Web Search Server — Search the web with multiple engines.

Uses DuckDuckGo (no API key required) with optional Brave Search support.
"""

import json
import urllib.request
import urllib.parse
import re
from html import unescape

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("web-search")


def _ddg_search(query: str, count: int = 5) -> list:
    """Search via DuckDuckGo HTML lite."""
    url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; MCPHub/0.1)"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    results = []
    # Parse simple results from lite version
    links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]+)</a>', html)
    seen = set()
    for url, title in links:
        if "duckduckgo" in url:
            continue
        clean_url = url.split("?")[0]
        if clean_url in seen:
            continue
        seen.add(clean_url)
        results.append({
            "title": unescape(title).strip(),
            "url": clean_url,
        })
        if len(results) >= count:
            break
    return results


def _fetch_page(url: str, max_chars: int = 5000) -> str:
    """Fetch and extract readable text from a URL."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; MCPHub/0.1)"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read(100_000).decode("utf-8", errors="replace")

    # Simple text extraction (strip HTML tags)
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="web_search",
            description="Search the web using DuckDuckGo. No API key required.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "count": {"type": "integer", "description": "Number of results (1-10)", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="fetch_url",
            description="Fetch content from a URL and return readable text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"},
                    "max_chars": {"type": "integer", "description": "Max characters to return", "default": 5000}
                },
                "required": ["url"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "web_search":
        count = min(max(arguments.get("count", 5), 1), 10)
        results = _ddg_search(arguments["query"], count)
        if not results:
            return [TextContent(type="text", text="No results found.")]
        lines = [f"🔍 Search results for: {arguments['query']}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r['title']}**\n   {r['url']}\n")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "fetch_url":
        max_chars = arguments.get("max_chars", 5000)
        text = _fetch_page(arguments["url"], max_chars)
        return [TextContent(type="text", text=f"📄 Content from {arguments['url']}:\n\n{text}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
