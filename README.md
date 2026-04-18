# 🔌 MCP Hub

**A curated collection of production-ready MCP servers. Plug-and-play tools for Claude, Cursor, Windsurf & more.**

[![GitHub Stars](https://img.shields.io/github/stars/4Artursmith/mcp-hub?style=social)](https://github.com/4Artursmith/mcp-hub)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io)

> Stop writing MCP servers from scratch. Ship in seconds, not hours.

```
📦 20+ ready-to-use MCP servers
⚡ One-line install
🔌 Works with Claude Desktop, Cursor, Windsurf, Zed & more
🛠️ Customizable & extensible
```

---

## 🚀 Quick Start

```bash
pip install mcp-hub
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["-m", "mcp_hub.server_weather"]
    }
  }
}
```

### Cursor / Windsurf

```json
{
  "mcp": {
    "servers": {
      "weather": {
        "command": "python",
        "args": ["-m", "mcp_hub.server_weather"]
      }
    }
  }
}
```

Restart your editor. That's it. 🎉

---

## 📦 Available Servers

| Server | Description | Install |
|--------|-------------|---------|
| 🌤️ [Weather](#weather) | Real-time weather & forecasts | `mcp_hub.server_weather` |
| 🔍 [Web Search](#web-search) | Search the web with multiple engines | `mcp_hub.server_web_search` |
| 🐙 [GitHub](#github) | Repo management, issues, PRs, code search | `mcp_hub.server_github` |
| 💰 [Crypto](#crypto) | Live prices, charts, market data | `mcp_hub.server_crypto` |
| 🖥️ [System](#system) | System info, processes, file ops | `mcp_hub.server_system` |
| 🐳 [Docker](#docker) | Container management & monitoring | `mcp_hub.server_docker` |
| 🗄️ [Database](#database) | SQL queries, schema inspection | `mcp_hub.server_database` |
| 📧 [Email](#email) | Send & read emails via SMTP/IMAP | `mcp_hub.server_email` |
| 📅 [Calendar](#calendar) | Google Calendar integration | `mcp_hub.server_calendar` |
| 📝 [Notes](#notes) | Obsidian/Markdown note management | `mcp_hub.server_notes` |
| 🌐 [HTTP](#http) | Make HTTP requests, scrape pages | `mcp_hub.server_http` |
| 📊 [CSV](#csv) | Analyze & transform CSV/Excel files | `mcp_hub.server_csv` |
| 🗺️ [Maps](#maps) | Geocoding, routes, places | `mcp_hub.server_maps` |
| 🐦 [Twitter](#twitter) | Post tweets, search, get profiles | `mcp_hub.server_twitter` |
| 💬 [Slack](#slack) | Send messages, read channels | `mcp_hub.server_slack` |
| 🎵 [Spotify](#spotify) | Search tracks, playlists, playback | `mcp_hub.server_spotify` |
| 📸 [Screenshot](#screenshot) | Take webpage screenshots | `mcp_hub.server_screenshot` |
| 🔐 [Passwords](#passwords) | Bitwarden/1Password integration | `mcp_hub.server_passwords` |
| 📁 [Files](#files) | Advanced file operations & search | `mcp_hub.server_files` |
| ⏰ [Reminder](#reminder) | Set reminders & notifications | `mcp_hub.server_reminder` |

---

## 🌤️ Weather

Get current weather and forecasts for any location worldwide.

```python
# Tools available:
- get_current_weather(location: str) -> dict
- get_forecast(location: str, days: int = 5) -> list
- get_air_quality(lat: float, lon: float) -> dict
```

**Example prompt:** *"What's the weather in Tokyo right now?"*

---

## 🔍 Web Search

Search the web using DuckDuckGo. No API key required.

```python
# Tools available:
- web_search(query: str, count: int = 5) -> list
- fetch_url(url: str) -> str
- extract_text(url: str) -> str
```

**Example prompt:** *"Search for the latest news about AI agents"*

---

## 🐙 GitHub

Full GitHub integration — repos, issues, PRs, code search, and more.

```python
# Tools available:
- list_repos(username: str) -> list
- get_repo(owner: str, repo: str) -> dict
- list_issues(owner: str, repo: str, state: str) -> list
- create_issue(owner: str, repo: str, title: str, body: str) -> dict
- search_code(query: str) -> list
- get_file_content(owner: str, repo: str, path: str) -> str
```

**Example prompt:** *"Show me open issues in the react repo"*

---

## 💰 Crypto

Live cryptocurrency prices, market data, and charts.

```python
# Tools available:
- get_price(symbol: str) -> dict
- get_market_data(symbol: str) -> dict
- get_trending() -> list
- get_price_history(symbol: str, days: int) -> list
```

**Example prompt:** *"What's the current price of Bitcoin?"*

---

## 🖥️ System

System information, process monitoring, and file operations.

```python
# Tools available:
- get_system_info() -> dict
- list_processes(sort_by: str) -> list
- get_disk_usage() -> dict
- get_network_info() -> dict
- run_command(cmd: str) -> str
```

---

## 🐳 Docker

Manage Docker containers, images, and volumes.

```python
# Tools available:
- list_containers(all: bool) -> list
- get_container_logs(name: str, tail: int) -> str
- get_container_stats(name: str) -> dict
- list_images() -> list
- inspect_container(name: str) -> dict
```

---

## 🗄️ Database

Query and inspect SQL databases (SQLite, PostgreSQL, MySQL).

```python
# Tools available:
- execute_query(connection: str, query: str) -> list
- list_tables(connection: str) -> list
- describe_table(connection: str, table: str) -> dict
- get_schema(connection: str) -> dict
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token | For GitHub server |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | For Weather server |
| `BRAVE_API_KEY` | Brave Search API key | Optional for Web Search |
| `COINMARKETCAP_API_KEY` | CoinMarketCap API key | Optional for Crypto |
| `SMTP_HOST` | SMTP server host | For Email server |
| `SLACK_TOKEN` | Slack bot token | For Slack server |

### Run Multiple Servers

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["-m", "mcp_hub.server_weather"]
    },
    "search": {
      "command": "python",
      "args": ["-m", "mcp_hub.server_web_search"]
    },
    "github": {
      "command": "python",
      "args": ["-m", "mcp_hub.server_github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "crypto": {
      "command": "python",
      "args": ["-m", "mcp_hub.server_crypto"]
    }
  }
}
```

---

## 🛠️ Create Your Own Server

MCP Hub servers follow a simple pattern:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="my_tool",
            description="Does something cool",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                },
                "required": ["input"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "my_tool":
        result = do_something(arguments["input"])
        return [TextContent(type="text", text=result)]

# Run with stdio transport
from mcp.server.stdio import stdio_server

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 📊 Why MCP Hub?

| Feature | MCP Hub | Building from scratch |
|---------|---------|----------------------|
| Time to deploy | ⚡ Seconds | 🐢 Hours/Days |
| Production-ready | ✅ Yes | ❌ Needs work |
| Multiple services | ✅ 20+ servers | ❌ One at a time |
| Documentation | ✅ Complete | ❌ DIY |
| Maintenance | ✅ Community | ❌ All on you |

---

## 🗺️ Roadmap

- [ ] 30+ MCP servers
- [ ] GUI configuration tool
- [ ] Docker Compose for all servers
- [ ] Server marketplace & discovery
- [ ] Plugin system for custom servers
- [ ] MCP Inspector integration
- [ ] Server health monitoring dashboard

---

## 🤝 Contributing

Contributions welcome! Add your own MCP server in 3 steps:

1. Create `mcp_hub/server_yourname.py`
2. Follow the [template](#create-your-own-server)
3. Open a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## ⭐ Star History

If you find MCP Hub useful, please give it a star! It helps others discover the project.

[![Star History Chart](https://api.star-history.com/svg?repos=4Artursmith/mcp-hub&type=Date)](https://star-history.com/#4Artursmith/mcp-hub&Date)

---

## 📄 License

MIT © [4Artursmith](https://github.com/4Artursmith)

---

<p align="center">
  <b>Made with ❤️ for the MCP community</b>
</p>
