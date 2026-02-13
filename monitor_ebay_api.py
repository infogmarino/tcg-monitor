import os
import requests
import json
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

PRODUCTS_FILE = "products.json"
MAX_STORED = 6  # salva solo ultimi 6 per query


def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return {}
    try:
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_products(data):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)


def search_sold_items(query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {EBAY_TOKEN}",
        "Content-Type": "application/json",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }

    params = {
        "q": query,
        "filter": "soldItemsOnly:true",
        "sort": "newlyListed",
        "limit": "10"
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

    if not EBAY_TOKEN or not BOT_TOKEN or not CHAT_ID:
        print("Chiavi mancanti.")
        return

    products = load_products()
    updated = False
    new_messages = []

    for query in QUERIES:
        print(f"--- Query: {query} ---")
        items = search_sold_items(query)

        if query not in products:
            products[query] = []

        stored_ids = set(products[query])

        for item in items:
            item_id = item["itemId"]

            if item_id not in stored_ids:
                title = item["title"]
                price = item.get("price", {}).get("value", "N/A")
                currency = item.get("price", {}).get("currency", "")
                url = item.get("itemWebUrl", "")

                message = (
                    f"🔥 NUOVO VENDUTO\n"
                    f"{title}\n"
                    f"{price} {currency}\n"
                    f"{url}"
                )

                new_messages.append(message)

                products[query].insert(0, item_id)
                updated = True

        # mantieni solo ultimi MAX_STORED
        products[query] = products[query][:MAX_STORED]

    if updated:
        save_products(products)

        for msg in new_messages:
            send_telegram(msg)

        print("Nuovi venduti trovati:", len(new_messages))
    else:
        print("Nessun nuovo venduto.")


if __name__ == "__main__":
    main()