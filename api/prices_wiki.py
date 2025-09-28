from fastapi import HTTPException
import asyncio
import aiohttp
from typing import Dict, List, Optional

PRICES_BASE_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
TIMESERIES_BASE_URL = "https://prices.runescape.wiki/api/v1/osrs/timeseries"
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


async def fetch_timeseries(item_id: int, timestep: Optional[str] = "5m"):
    """
    Fetch the price candles for a given item_id with an optional timestep, 5m default.
    :param item_id: int id for the item to fetch
    :param timestep: duration of timestep, defaults to 5m, can be up to 1d
    :return: JSON mapping of time series entries for item_id
    """
    url = f"{TIMESERIES_BASE_URL}&timestep={timestep}?id={item_id}"

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=resp.status, detail="Error fetching timeseries"
                )
            return await resp.json()


async def fetch_timeseries_for_set(item_dict: Dict[str, List[int]], timestep: str = "5m"):
    """
    Fetch timeseries for all item IDs and combine them into aggregated candles.
    Backfill with first non-zero entry and forward-fill subsequent missing values.
    """
    async with aiohttp.ClientSession(headers=HEADERS) as session:

        async def get_series(item_id: int):
            url = f"{TIMESERIES_BASE_URL}?id={item_id}&timestep={timestep}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(
                        status_code=resp.status,
                        detail=f"Error fetching timeseries for {item_id}"
                    )
                data = await resp.json()
                return data.get("data", [])

        tasks = [
            asyncio.create_task(get_series(i_id))
            for item_ids in item_dict.values()
            for i_id in item_ids
        ]
        results = await asyncio.gather(*tasks)

    # Build a set of all timestamps across all series
    all_timestamps = sorted({entry["timestamp"] for series in results for entry in series})

    filled_series = []
    for series in results:
        filled = {}
        last_entry = None  # will hold the last valid entry
        first_entry = None  # will hold the first non-zero entry
        series_idx = 0

        # Identify the first non-zero entry
        for entry in series:
            if any(entry.get(key) not in (0, None) for key in ["avgHighPrice","avgLowPrice","highPriceVolume","lowPriceVolume"]):
                first_entry = {k: entry.get(k, 0) for k in ["avgHighPrice","avgLowPrice","highPriceVolume","lowPriceVolume"]}
                break
        if not first_entry:
            first_entry = {k: 0 for k in ["avgHighPrice","avgLowPrice","highPriceVolume","lowPriceVolume"]}

        for ts in all_timestamps:
            if series_idx < len(series) and series[series_idx]["timestamp"] == ts:
                current = series[series_idx]
                if last_entry is None:
                    last_entry = first_entry.copy()
                for key in last_entry:
                    val = current.get(key)
                    if val not in (0, None):
                        last_entry[key] = val
                series_idx += 1
            elif last_entry is None:
                # backfill before first entry
                last_entry = first_entry.copy()
            filled[ts] = last_entry.copy()

        filled_series.append(filled)

    # Combine candles
    combined: List[Dict[str, int]] = []
    for ts in all_timestamps:
        candle = {
            "timestamp": ts,
            "avgHighPrice": 0,
            "avgLowPrice": 0,
            "highPriceVolume": 0,
            "lowPriceVolume": 0,
        }
        for series in filled_series:
            entry = series[ts]
            candle["avgHighPrice"] += entry.get("avgHighPrice") or 0
            candle["avgLowPrice"] += entry.get("avgLowPrice") or 0
            candle["highPriceVolume"] += entry.get("highPriceVolume") or 0
            candle["lowPriceVolume"] += entry.get("lowPriceVolume") or 0

        combined.append(candle)

    return {"data": combined}
