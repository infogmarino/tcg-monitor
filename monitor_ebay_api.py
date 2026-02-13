import os
import requests
import json
import time
from datetime import datetime

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_TOKEN = os.getenv("EBAY_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SEARCH_TERMS = [
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


def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return {}
    try:
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })


def search_sold_items(query):
    url = "https://svcs.ebay.com/services/search/FindingService/v1"

    headers = {
        "X-EBAY-SOA-OPERATION-NAME": "findCompletedItems",
        "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON"
    }

    params = {
        "keywords": query,
        "itemFilter(0).name": "SoldItemsOnly",
        "itemFilter(0).value": "true",
        "sortOrder": "EndTimeSoonest",
        "paginationInput.entriesPerPage": "10"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore eBay:", response.status_code)
        return []

    data = response.json()

    try:
        items = data["findCompletedItemsResponse"][0]["searchResult"][0]["item"]
    except:
        return []

    return items


def main():
    print("Controllo venduti:", datetime.now())

    products = load_products()
    first_run = len(products) == 0

    new_products = {}

    for term in SEARCH_TERMS:
        print(f"--- Query: {term} ---")

        items = search_sold_items(term)

        for item in items:
            item_id = item["itemId"][0]

            if item_id not in products:
                new_products[item_id] = {
                    "title": item["title"][0],
                    "price": item["sellingStatus"][0]["currentPrice"][0]["__value__"],
                    "currency": item["sellingStatus"][0]["currentPrice"][0]["@currencyId"],
                    "url": item["viewItemURL"][0]
                }

        time.sleep(2)  # pausa anti-rate limit

    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        products.update(new_products)
        save_products(products)
        print("Inizializzazione completata.")
        return

    if new_products:
        for p in new_products.values():
            message = f"🟢 NUOVO VENDUTO\n{p['title']}\n{p['price']} {p['currency']}\n{p['url']}"
            send_telegram(message)

        products.update(new_products)
        save_products(products)
        print("Nuovi venduti notificati.")
    else:
        print("Nessun nuovo venduto.")


if __name__ == "__main__":
    main()