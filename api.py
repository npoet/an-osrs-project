import requests
from typing import Dict, Any

PRICES_BASE_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
USER_AGENT = "python-requests - @npoet on discord"
HEADERS = {"User-Agent": USER_AGENT}

ITEM_DICT = {
    "Avernic treads (max)": [31088, 13239, 13237, 13235],
    "Imbued zamorak cape (deadman)": [29628],
    "Confliction gauntlets": [31106],
    "Oathplate chest": [30753],
    "Oathplate legs": [30756],
    "Amulet of rancour": [29801],
    "Dinh's blazing bulwark": [21015, 28684],
    "Celestial signet": [23943],
}


def get_price(item_id: int) -> int:
    """
    returns the high price for a given item_id from the osrs prices wiki
    :param item_id: integer id of the item to get prices for
    :return: high price for given item_id (int)
    """
    req = requests.get(PRICES_BASE_URL + f"?id={item_id}", headers=HEADERS).json()
    return req["data"][str(item_id)]["high"]


def get_total_price(items: Dict[str, Any]) -> int:
    """
    returns the total price for a given items dictionary from the osrs prices wiki
    :param items: a mapping of item names to their component ids
    :return: a total price for the given items (int)
    """
    total_price = 0
    for item in items.values():
        temp_price = 0
        for i_id in item:
            price = get_price(i_id)
            temp_price += price
        total_price += temp_price
    return total_price


if __name__ == "__main__":
    print(get_total_price(ITEM_DICT))
