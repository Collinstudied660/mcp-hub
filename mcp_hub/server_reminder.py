"""⏰ MCP Reminder Server — Set reminders & timers."""

import json
import time
import threading
import os
import signal

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("reminder")

reminders = {}
_counter = 0
_lock = threading.Lock()


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="set_reminder",
            description="Set a reminder that fires after a specified number of seconds.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Reminder message"},
                    "seconds": {"type": "integer", "description": "Seconds until reminder fires"}
                },
                "required": ["message", "seconds"]
            }
        ),
        Tool(
            name="list_reminders",
            description="List all active reminders.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="cancel_reminder",
            description="Cancel a reminder by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "reminder_id": {"type": "integer", "description": "Reminder ID"}
                },
                "required": ["reminder_id"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    global _counter

    if name == "set_reminder":
        with _lock:
            _counter += 1
            rid = _counter

        msg = arguments["message"]
        secs = arguments["seconds"]

        def fire():
            time.sleep(secs)
            with _lock:
                if rid in reminders:
                    print(f"\n⏰ REMINDER: {msg}\n", flush=True)
                    del reminders[rid]

        t = threading.Thread(target=fire, daemon=True)
        with _lock:
            reminders[rid] = {"thread": t, "message": msg, "seconds": secs, "created": time.time()}
        t.start()

        text = f"⏰ Reminder #{rid} set: \"{msg}\" in {secs}s"
        return [TextContent(type="text", text=text)]

    elif name == "list_reminders":
        with _lock:
            if not reminders:
                return [TextContent(type="text", text="No active reminders.")]
            lines = ["⏰ Active reminders:\n"]
            for rid, r in reminders.items():
                elapsed = int(time.time() - r["created"])
                remaining = max(0, r["seconds"] - elapsed)
                lines.append(f"  #{rid}: \"{r['message']}\" — {remaining}s remaining")
            return [TextContent(type="text", text="\n".join(lines))]

    elif name == "cancel_reminder":
        rid = arguments["reminder_id"]
        with _lock:
            if rid in reminders:
                del reminders[rid]
                return [TextContent(type="text", text=f"✅ Reminder #{rid} cancelled.")]
            else:
                return [TextContent(type="text", text=f"❌ Reminder #{rid} not found.")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
