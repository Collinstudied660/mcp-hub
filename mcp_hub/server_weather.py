"""🌤️ MCP Weather Server — Real-time weather & forecasts.

Uses Open-Meteo (free, no API key required) and wttr.in as fallback.
"""

import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("weather")


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MCPHub/0.1"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _geocode(location: str) -> dict:
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location)}&count=1"
    data = _fetch_json(url)
    if not data.get("results"):
        raise ValueError(f"Location not found: {location}")
    r = data["results"][0]
    return {"lat": r["latitude"], "lon": r["longitude"], "name": r.get("name", location),
            "country": r.get("country", "")}


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather for any location worldwide. No API key needed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name, e.g. 'Tokyo' or 'New York'"}
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="get_forecast",
            description="Get weather forecast for up to 7 days.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "description": "Number of days (1-7)", "default": 5}
                },
                "required": ["location"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_current_weather":
        geo = _geocode(arguments["location"])
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={geo['lat']}&longitude={geo['lon']}"
               f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto")
        data = _fetch_json(url)
        cur = data["current"]

        WMO = {0: "☀️ Clear", 1: "🌤️ Mainly clear", 2: "⛅ Partly cloudy", 3: "☁️ Overcast",
               45: "🌫️ Fog", 48: "🌫️ Rime fog", 51: "🌦️ Light drizzle", 53: "🌦️ Drizzle",
               55: "🌧️ Heavy drizzle", 61: "🌧️ Light rain", 63: "🌧️ Rain", 65: "🌧️ Heavy rain",
               71: "🌨️ Light snow", 73: "🌨️ Snow", 75: "🌨️ Heavy snow", 80: "🌦️ Light showers",
               81: "🌧️ Showers", 82: "🌧️ Heavy showers", 95: "⛈️ Thunderstorm"}

        weather = WMO.get(cur.get("weather_code", 0), "🌡️ Unknown")
        text = (
            f"📍 {geo['name']}, {geo['country']}\n"
            f"{weather}\n"
            f"🌡️ Temperature: {cur['temperature_2m']}°C\n"
            f"💧 Humidity: {cur['relative_humidity_2m']}%\n"
            f"💨 Wind: {cur['wind_speed_10m']} km/h\n"
            f"🕐 Updated: {cur['time']}"
        )
        return [TextContent(type="text", text=text)]

    elif name == "get_forecast":
        days = min(max(arguments.get("days", 5), 1), 7)
        geo = _geocode(arguments["location"])
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={geo['lat']}&longitude={geo['lon']}"
               f"&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum"
               f"&timezone=auto&forecast_days={days}")
        data = _fetch_json(url)
        daily = data["daily"]

        WMO = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 51: "🌦️", 61: "🌧️",
               63: "🌧️", 71: "🌨️", 73: "🌨️", 80: "🌦️", 95: "⛈️"}

        lines = [f"📍 {geo['name']}, {geo['country']} — {days}-day forecast:\n"]
        for i in range(len(daily["time"])):
            icon = WMO.get(daily["weather_code"][i], "🌡️")
            lines.append(
                f"{daily['time'][i]}: {icon} {daily['temperature_2m_min'][i]}°C → "
                f"{daily['temperature_2m_max'][i]}°C | 💧 {daily['precipitation_sum'][i]}mm"
            )
        return [TextContent(type="text", text="\n".join(lines))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
