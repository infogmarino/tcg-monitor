import os
import requests
import json
from datetime import datetime, timedelta

EBAY_CLIENT_ID = os.environ.get("EBAY_APP_ID")
EBAY_CLIENT_SECRET = os.environ.get("EBAY_CERT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID")

SEARCH_TERMS = [
    "Charizard psa 10",
    "Magikarp psa 10",
    "Eevee psa 10",
    "Mew psa 10",
    "Umbreon psa 10",
    "Chinese psa 10",
    "Pokemon Jp psa 10",
    "Snorlax psa 10",
    "Pikachu psa 10"
]

EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

def get_access_token():
    response = requests.post(
        EBAY_TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        },
        auth=(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET)
    )
    return response.json()["access_token"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })

def load_seen_items():
    try:
        with open("seen_items.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_seen_items(items):
    with open("seen_items.json", "w") as f:
        json.dump(items, f)

def check_ebay():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    seen_items = load_seen_items()
    new_seen = seen_items.copy()

    for term in SEARCH_TERMS:
        response = requests.get(
            EBAY_SEARCH_URL,
            headers=headers,
            params={
                "q": term,
                "filter": "buyingOptions:{FIXED_PRICE},conditions:{USED},itemEndDate:[NOW-1HOUR..NOW]",
                "sort": "-itemEndDate",
                "limit": 20
            }
        )

        data = response.json()

        if "itemSummaries" not in data:
            continue

        for item in data["itemSummaries"]:
            item_id = item["itemId"]

            if item_id not in seen_items:
                title = item["title"]
                price = item["price"]["value"]
                currency = item["price"]["currency"]
                url = item["itemWebUrl"]

                message = f"🔥 <b>NUOVA VENDITA</b>\n\n{title}\n💰 {price} {currency}\n🔗 {url}"
                send_telegram(message)

                new_seen.append(item_id)

    save_seen_items(new_seen)

if __name__ == "__main__":
    print("Monitor eBay avviato...")
    check_ebay()
