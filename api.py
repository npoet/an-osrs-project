import asyncio
import aiohttp
from typing import Dict, Any

PRICES_BASE_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
# Descriptive user-agent per wiki guidelines, don't add me on discord
USER_AGENT = "aiohttp - @npoet on discord"
HEADERS = {"User-Agent": USER_AGENT}

ITEM_DICT = {
    "Avernic treads (max)": [31088, 13239, 13237, 13235],   # Avernic treads + Prims + Pegs + Eternals
    "Imbued zamorak cape (deadman)": [29628],   # Armageddon cape fabric
    "Confliction gauntlets": [31106],
    "Oathplate chest": [30753],
    "Oathplate legs": [30756],
    "Amulet of rancour": [29801],
    "Dinh's blazing bulwark": [21015, 28684],   # Dinh's bulwark + Trailblazer reloaded bulwark orn kit
    "Celestial signet": [23943],    # Elven signet
}


async def get_price(session: aiohttp.ClientSession, item_id: int) -> int:
    """
    Fetch the high price for a given item_id.
    :param session: async client session
    :param item_id: int id for the item to fetch
    :return: today's high price (int)
    """
    async with session.get(f"{PRICES_BASE_URL}?id={item_id}") as resp:
        data = await resp.json()
        return data["data"][str(item_id)]["high"]


async def get_total_price(items: Dict[str, Any]) -> int:
    """
    Fetch prices for all items concurrently and return total.
    :param items: mapping of item names to included ids
    :return: today's total high price (int)
    """
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [
            get_price(session, i_id)
            for item_ids in items.values()
            for i_id in item_ids
        ]
        results = await asyncio.gather(*tasks)
        return sum(results)


if __name__ == "__main__":
    # Calc total price and display as GP
    total = asyncio.run(get_total_price(ITEM_DICT))
    print(f"{total:,} gp")
