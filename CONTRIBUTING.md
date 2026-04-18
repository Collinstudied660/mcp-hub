# Contributing to MCP Hub

Thanks for your interest in contributing! 🎉

## Adding a New Server

1. Create a new file: `mcp_hub/server_yourname.py`
2. Follow this template:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("your-server-name")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="your_tool",
            description="What it does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "your_tool":
        result = do_something(arguments["param"])
        return [TextContent(type="text", text=result)]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

3. Add your server to the README table
4. Open a PR

## Guidelines

- **No external dependencies** in core servers (use stdlib only)
- Each server should be self-contained
- Include helpful error messages
- Use emojis in output for readability
- Test your server before submitting

## Development

```bash
pip install -e ".[dev]"
python -m mcp_hub.server_weather  # Test a server
```
