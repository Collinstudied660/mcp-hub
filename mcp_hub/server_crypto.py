"""💰 MCP Crypto Server — Live cryptocurrency prices & market data.

Uses CoinGecko free API (no key required).
"""

import json
import urllib.request

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("crypto")

COINGECKO = "https://api.coingecko.com/api/v3"

SYMBOL_MAP = {
    "btc": "bitcoin", "eth": "ethereum", "sol": "solana", "bnb": "binancecoin",
    "xrp": "ripple", "ada": "cardano", "doge": "dogecoin", "dot": "polkadot",
    "avax": "avalanche-2", "matic": "matic-network", "link": "chainlink",
    "uni": "uniswap", "ltc": "litecoin", "atom": "cosmos", "near": "near",
    "arbitrum": "arbitrum", "optimism": "optimism", "sui": "sui",
}


def _fetch_json(url: str) -> dict | list:
    req = urllib.request.Request(url, headers={"User-Agent": "MCPHub/0.1"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _resolve(symbol: str) -> str:
    s = symbol.lower().strip()
    return SYMBOL_MAP.get(s, s)


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_price",
            description="Get current price of a cryptocurrency in USD.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Crypto symbol, e.g. 'BTC', 'ETH', 'SOL'"}
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_market_data",
            description="Get detailed market data: price, market cap, volume, 24h change.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Crypto symbol"}
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_trending",
            description="Get currently trending cryptocurrencies.",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_price":
        cid = _resolve(arguments["symbol"])
        data = _fetch_json(f"{COINGECKO}/simple/price?ids={cid}&vs_currencies=usd")
        if cid not in data:
            return [TextContent(type="text", text=f"❌ Coin not found: {arguments['symbol']}")]
        price = data[cid]["usd"]
        return [TextContent(type="text", text=f"💰 {arguments['symbol'].upper()}: ${price:,.2f}")]

    elif name == "get_market_data":
        cid = _resolve(arguments["symbol"])
        data = _fetch_json(f"{COINGECKO}/coins/{cid}?localization=false&tickers=false"
                          f"&community_data=false&developer_data=false")
        md = data.get("market_data", {})
        text = (
            f"📊 {data['name']} ({data['symbol'].upper()})\n"
            f"💰 Price: ${md['current_price']['usd']:,.2f}\n"
            f"📈 24h Change: {md['price_change_percentage_24h']:.2f}%\n"
            f"🏦 Market Cap: ${md['market_cap']['usd']:,.0f}\n"
            f"📊 Volume 24h: ${md['total_volume']['usd']:,.0f}\n"
            f"🔝 ATH: ${md['ath']['usd']:,.2f}\n"
            f"📅 ATH Date: {md['ath_date']['usd'][:10]}"
        )
        return [TextContent(type="text", text=text)]

    elif name == "get_trending":
        data = _fetch_json(f"{COINGECKO}/search/trending")
        lines = ["🔥 Trending cryptocurrencies:\n"]
        for i, item in enumerate(data.get("coins", [])[:10], 1):
            c = item["item"]
            lines.append(f"{i}. {c['name']} ({c['symbol'].upper()}) — Score: {c['score']}")
        return [TextContent(type="text", text="\n".join(lines))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
