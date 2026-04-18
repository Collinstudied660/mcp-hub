"""🌐 MCP HTTP Server — Make HTTP requests, scrape pages, check APIs."""

import json
import urllib.request
import urllib.error
import re
from html import unescape

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("http")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="http_get",
            description="Make an HTTP GET request and return the response.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"},
                    "headers": {"type": "string", "description": "JSON object of headers"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="http_post",
            description="Make an HTTP POST request with JSON body.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to POST to"},
                    "body": {"type": "string", "description": "JSON body"},
                    "headers": {"type": "string", "description": "JSON object of headers"}
                },
                "required": ["url", "body"]
            }
        ),
        Tool(
            name="check_url",
            description="Check if a URL is reachable and get status code.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to check"}
                },
                "required": ["url"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "http_get":
        headers = {"User-Agent": "MCPHub/0.1"}
        if arguments.get("headers"):
            headers.update(json.loads(arguments["headers"]))
        req = urllib.request.Request(arguments["url"], headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read(100_000).decode("utf-8", errors="replace")
                content_type = resp.headers.get("Content-Type", "")
                text = f"✅ Status: {resp.status}\n📋 Content-Type: {content_type}\n\n{data[:5000]}"
        except urllib.error.HTTPError as e:
            text = f"❌ HTTP {e.code}: {e.reason}"
        except Exception as e:
            text = f"❌ Error: {str(e)}"
        return [TextContent(type="text", text=text)]

    elif name == "http_post":
        headers = {"User-Agent": "MCPHub/0.1", "Content-Type": "application/json"}
        if arguments.get("headers"):
            headers.update(json.loads(arguments["headers"]))
        body = arguments["body"].encode("utf-8")
        req = urllib.request.Request(arguments["url"], data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read(100_000).decode("utf-8", errors="replace")
                text = f"✅ Status: {resp.status}\n\n{data[:5000]}"
        except urllib.error.HTTPError as e:
            text = f"❌ HTTP {e.code}: {e.reason}"
        except Exception as e:
            text = f"❌ Error: {str(e)}"
        return [TextContent(type="text", text=text)]

    elif name == "check_url":
        req = urllib.request.Request(arguments["url"], method="HEAD",
                                     headers={"User-Agent": "MCPHub/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = f"✅ {arguments['url']} — HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            text = f"⚠️ {arguments['url']} — HTTP {e.code}: {e.reason}"
        except Exception as e:
            text = f"❌ {arguments['url']} — {str(e)}"
        return [TextContent(type="text", text=text)]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
