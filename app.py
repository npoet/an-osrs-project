from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List
import json
from pathlib import Path
from api.prices_wiki import fetch_prices
from api.utils import format_gp

# Load items.json at startup
ITEMS_FILE = Path(__file__).parent / "items.json"
with open(ITEMS_FILE, "r", encoding="utf-8") as f:
    ITEM_DICT: Dict[str, List[int]] = json.load(f)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://npoet.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/total")
async def get_total():
    """Return the grand total value of all items."""
    prices = await fetch_prices(ITEM_DICT)
    total = sum(prices.values())

    return {
        "total_raw": total,
        "total_formatted": f"{total:,} gp",
        "total_compact": format_gp(total),
    }


@app.get("/breakdown")
async def get_breakdown():
    """Return detailed breakdown of items + total."""
    prices = await fetch_prices(ITEM_DICT)

    breakdown: List[Dict[str, Any]] = []
    grand_total = 0

    for item_name, ids in ITEM_DICT.items():
        subtotal = sum(prices[i_id] for i_id in ids)
        grand_total += subtotal
        breakdown.append(
            {
                "item": item_name,
                "ids": ids,
                "subtotal_raw": subtotal,
                "subtotal_formatted": f"{subtotal:,} gp",
                "subtotal_compact": format_gp(subtotal),
            }
        )

    return {
        "items": breakdown,
        "total": {
            "raw": grand_total,
            "formatted": f"{grand_total:,} gp",
            "compact": format_gp(grand_total),
        },
    }
