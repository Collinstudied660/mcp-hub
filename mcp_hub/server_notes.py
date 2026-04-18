"""📝 MCP Notes Server — Manage Obsidian-style Markdown notes."""

import os
import json
import glob
import time
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("notes")

# Default vault directory
VAULT_DIR = os.environ.get("NOTES_VAULT_DIR", os.path.expanduser("~/notes"))


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="create_note",
            description="Create a new Markdown note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note content (Markdown)"},
                    "folder": {"type": "string", "description": "Subfolder", "default": ""}
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="read_note",
            description="Read a note by title or path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title or filename"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="search_notes",
            description="Search notes by content or title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_notes",
            description="List all notes in the vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "Subfolder to list", "default": ""}
                }
            }
        ),
    ]


def _vault():
    os.makedirs(VAULT_DIR, exist_ok=True)
    return VAULT_DIR


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    vault = _vault()

    if name == "create_note":
        folder = arguments.get("folder", "")
        title = arguments["title"]
        filename = title.lower().replace(" ", "-") + ".md"
        path = os.path.join(vault, folder, filename) if folder else os.path.join(vault, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        content = f"# {title}\n\n{arguments['content']}\n"
        with open(path, "w") as f:
            f.write(content)
        return [TextContent(type="text", text=f"📝 Note created: {path}")]

    elif name == "read_note":
        title = arguments["title"]
        # Try exact match first
        candidates = glob.glob(os.path.join(vault, "**", f"*{title}*"), recursive=True)
        md_files = [f for f in candidates if f.endswith(".md")]
        if not md_files:
            return [TextContent(type="text", text=f"❌ Note not found: {title}")]
        with open(md_files[0]) as f:
            content = f.read()
        return [TextContent(type="text", text=f"📄 {os.path.basename(md_files[0])}:\n\n{content}")]

    elif name == "search_notes":
        query = arguments["query"].lower()
        results = []
        for root, dirs, files in os.walk(vault):
            for fn in files:
                if fn.endswith(".md"):
                    filepath = os.path.join(root, fn)
                    try:
                        with open(filepath) as f:
                            content = f.read()
                        if query in fn.lower() or query in content.lower():
                            results.append(filepath)
                    except Exception:
                        pass
        if not results:
            return [TextContent(type="text", text=f"No notes found matching: {query}")]
        text = f"🔍 Found {len(results)} notes:\n\n"
        for r in results[:20]:
            text += f"  • {os.path.relpath(r, vault)}\n"
        return [TextContent(type="text", text=text)]

    elif name == "list_notes":
        folder = arguments.get("folder", "")
        search_dir = os.path.join(vault, folder) if folder else vault
        notes = []
        for root, dirs, files in os.walk(search_dir):
            for fn in files:
                if fn.endswith(".md"):
                    notes.append(os.path.relpath(os.path.join(root, fn), vault))
        if not notes:
            return [TextContent(type="text", text="No notes found.")]
        text = f"📝 Notes ({len(notes)}):\n\n"
        for n in sorted(notes):
            text += f"  • {n}\n"
        return [TextContent(type="text", text=text)]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
