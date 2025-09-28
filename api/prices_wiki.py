import asyncio
import aiohttp
from typing import Dict, List

PRICES_BASE_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
# Descriptive user-agent per wiki guidelines, don't add me on discord
USER_AGENT = "aiohttp - @npoet on discord"
HEADERS = {"User-Agent": USER_AGENT}


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


async def fetch_prices(item_dict: Dict[str, List[int]]) -> Dict[int, int]:
    """
    Fetch prices for all items concurrently and return info.
    :return: mapping of ids to prices
    """
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = {
            i_id: asyncio.create_task(get_price(session, i_id))
            for item_ids in item_dict.values()
            for i_id in item_ids
        }
        return {i_id: await task for i_id, task in tasks.items()}
