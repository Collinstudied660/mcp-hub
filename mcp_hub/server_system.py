"""🖥️ MCP System Server — System info, processes, file operations."""

import json
import os
import platform
import subprocess
import shutil

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("system")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_system_info",
            description="Get system information: OS, CPU, memory, disk.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_processes",
            description="List running processes sorted by CPU or memory usage.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sort_by": {"type": "string", "enum": ["cpu", "memory"], "default": "cpu"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="get_disk_usage",
            description="Get disk usage for all mounted filesystems.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="run_command",
            description="Run a shell command and return output. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="find_files",
            description="Find files matching a pattern.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Filename pattern, e.g. '*.py'"},
                    "path": {"type": "string", "description": "Directory to search", "default": "."}
                },
                "required": ["pattern"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_system_info":
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "cpu_count": os.cpu_count(),
        }
        # Memory
        try:
            with open("/proc/meminfo") as f:
                mem = {}
                for line in f:
                    parts = line.split()
                    if parts[0] in ("MemTotal:", "MemAvailable:", "SwapTotal:"):
                        mem[parts[0].rstrip(":")] = f"{int(parts[1]) // 1024} MB"
            info["memory"] = mem
        except Exception:
            pass

        text = "🖥️ System Information:\n"
        for k, v in info.items():
            if isinstance(v, dict):
                text += f"\n  {k}:\n"
                for sk, sv in v.items():
                    text += f"    {sk}: {sv}\n"
            else:
                text += f"  {k}: {v}\n"
        return [TextContent(type="text", text=text)]

    elif name == "list_processes":
        sort_flag = "-%mem" if arguments.get("sort_by") == "memory" else "-%cpu"
        limit = arguments.get("limit", 10)
        result = subprocess.run(
            ["ps", "aux", f"--sort={sort_flag}"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split("\n")
        header = lines[0]
        body = lines[1:limit + 1]
        text = f"📋 Top {limit} processes by {arguments.get('sort_by', 'cpu')}:\n\n{header}\n" + "\n".join(body)
        return [TextContent(type="text", text=text)]

    elif name == "get_disk_usage":
        result = subprocess.run(["df", "-h"], capture_output=True, text=True, timeout=10)
        return [TextContent(type="text", text=f"💾 Disk Usage:\n\n{result.stdout}")]

    elif name == "run_command":
        result = subprocess.run(
            arguments["command"], shell=True,
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        return [TextContent(type="text", text=output[:5000] or "(no output)")]

    elif name == "find_files":
        path = arguments.get("path", ".")
        result = subprocess.run(
            ["find", path, "-name", arguments["pattern"], "-maxdepth", "5"],
            capture_output=True, text=True, timeout=15
        )
        files = result.stdout.strip().split("\n")[:50]
        return [TextContent(type="text", text=f"📁 Found {len(files)} files:\n" + "\n".join(files))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
