import requests
import json
import os
from datetime import datetime

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
EBAY_TOKEN = os.getenv("EBAY_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

QUERIES = [
    "Charizard psa 10",
    "Pikachu psa 10",
    "Chinese psa 10",
    "Pokemon Jp psa 10",
    "Umbreon psa 10",
    "Gengar psa 10",
    "Celebrations psa 10",
    "Eevee psa 10",
    "Snorlax psa 10"
]

MAX_STORED = 5  # Manteniamo solo ultimi 5 per query


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, data=data)


def load_products():
    if not os.path.exists("products.json"):
        return {}
    with open("products.json", "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_products(data):
    with open("products.json", "w") as f:
        json.dump(data, f, indent=2)


def search_sold(query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {EBAY_TOKEN}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }

    params = {
        "q": query,
        "filter": "soldItemsOnly:true",
        "limit": 10,
        "sort": "-price"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore eBay:", response.status_code)
        print(response.text)
        return []

    data = response.json()
    return data.get("itemSummaries", [])


def main():
    print("Controllo venduti:", datetime.now())

    products = load_products()
    new_sales = []

    for query in QUERIES:
        print(f"--- Query: {query} ---")

        items = search_sold(query)

        if query not in products:
            products[query] = []

        stored_ids = products[query]

        for item in items:
            item_id = item["itemId"]

            if item_id not in stored_ids:
                title = item.get("title", "")
                price = item.get("price", {}).get("value", "")
                currency = item.get("price", {}).get("currency", "")
                url = item.get("itemWebUrl", "")

                message = (
                    f"🔥 <b>NUOVO VENDUTO</b>\n\n"
                    f"<b>{title}</b>\n"
                    f"💰 {price} {currency}\n"
                    f"{url}"
                )

                new_sales.append(message)
                stored_ids.append(item_id)

        # Manteniamo solo ultimi MAX_STORED
        products[query] = stored_ids[-MAX_STORED:]

    save_products(products)

    if new_sales:
        print("Nuovi venduti trovati:", len(new_sales))
        for msg in new_sales:
            send_telegram(msg)
    else:
        print("Nessun nuovo venduto.")


if __name__ == "__main__":
    main()