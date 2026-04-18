"""📊 MCP CSV Server — Analyze & transform CSV/Excel files."""

import csv
import json
import os
import io

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("csv")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="read_csv",
            description="Read a CSV file and return its contents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to CSV file"},
                    "rows": {"type": "integer", "description": "Max rows to return", "default": 50}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="csv_info",
            description="Get CSV file info: columns, row count, data types, sample data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to CSV file"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="csv_query",
            description="Query CSV with SQL-like operations (filter, sort, aggregate).",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to CSV file"},
                    "filter": {"type": "string", "description": "Python expression to filter rows, e.g. \"age > 30\""},
                    "columns": {"type": "string", "description": "Comma-separated columns to include"},
                    "sort_by": {"type": "string", "description": "Column to sort by"},
                    "limit": {"type": "integer", "default": 100}
                },
                "required": ["path"]
            }
        ),
    ]


def _read_csv(path: str, max_rows: int = None) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = []
        for i, row in enumerate(reader):
            if max_rows and i >= max_rows:
                break
            rows.append(row)
    return headers, rows


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    path = arguments["path"]

    if name == "read_csv":
        max_rows = arguments.get("rows", 50)
        headers, rows = _read_csv(path, max_rows)
        text = f"📄 {os.path.basename(path)} — showing {len(rows)} rows\n\n"
        text += " | ".join(headers) + "\n"
        text += "-" * 60 + "\n"
        for row in rows:
            text += " | ".join(str(row.get(h, "")) for h in headers) + "\n"
        return [TextContent(type="text", text=text)]

    elif name == "csv_info":
        headers, rows = _read_csv(path)
        file_size = os.path.getsize(path)

        # Detect types
        type_samples = {}
        for h in headers:
            vals = [r[h] for r in rows[:100] if r.get(h)]
            if all(v.replace(".", "").replace("-", "").isdigit() for v in vals if v):
                type_samples[h] = "number"
            else:
                type_samples[h] = "string"

        text = (
            f"📊 CSV Info: {os.path.basename(path)}\n"
            f"  📁 Size: {file_size:,} bytes\n"
            f"  📏 Rows: {len(rows)}\n"
            f"  📋 Columns: {len(headers)}\n\n"
            f"  Columns:\n"
        )
        for h in headers:
            text += f"    • {h} ({type_samples.get(h, 'unknown')})\n"

        text += f"\n  First 3 rows:\n"
        for row in rows[:3]:
            text += f"    {dict(list(row.items())[:5])}\n"

        return [TextContent(type="text", text=text)]

    elif name == "csv_query":
        headers, rows = _read_csv(path)
        result = rows

        # Filter
        if arguments.get("filter"):
            expr = arguments["filter"]
            filtered = []
            for row in result:
                try:
                    local = {k: _try_num(v) for k, v in row.items()}
                    if eval(expr, {"__builtins__": {}}, local):
                        filtered.append(row)
                except Exception:
                    pass
            result = filtered

        # Select columns
        if arguments.get("columns"):
            cols = [c.strip() for c in arguments["columns"].split(",")]
            result = [{c: r.get(c, "") for c in cols} for r in result]

        # Sort
        if arguments.get("sort_by"):
            col = arguments["sort_by"]
            result.sort(key=lambda r: _try_num(r.get(col, "")))

        limit = arguments.get("limit", 100)
        result = result[:limit]

        text = f"🔍 Query result: {len(result)} rows\n\n"
        text += json.dumps(result, indent=2, ensure_ascii=False)[:5000]
        return [TextContent(type="text", text=text)]


def _try_num(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return v


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
