import requests
import json
import os
import time
from datetime import datetime

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
EBAY_TOKEN = os.getenv("EBAY_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SEARCH_QUERIES = [
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

EBAY_API_URL = "https://svcs.ebay.com/services/search/FindingService/v1"


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message[:4000]
    }
    requests.post(url, data=payload)


def load_products():
    if not os.path.exists("products.json"):
        return {}

    try:
        with open("products.json", "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except:
        return {}


def save_products(products):
    with open("products.json", "w") as f:
        json.dump(products, f, indent=4)


def search_sold_items(query):
    params = {
        "OPERATION-NAME": "findCompletedItems",
        "SERVICE-VERSION": "1.13.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "REST-PAYLOAD": "",
        "keywords": query,
        "itemFilter(0).name": "SoldItemsOnly",
        "itemFilter(0).value": "true",
        "paginationInput.entriesPerPage": "10"
    }

    for attempt in range(3):
        response = requests.get(EBAY_API_URL, params=params)

        if response.status_code == 200:
            return response.json()

        print("Errore eBay:", response.status_code)
        time.sleep(3)

    return None


def main():
    print("Controllo venduti:", datetime.now())

    if not EBAY_APP_ID:
        print("Chiavi eBay mancanti.")
        return

    saved_products = load_products()
    new_products = {}
    first_run = len(saved_products) == 0

    for query in SEARCH_QUERIES:
        print(f"--- Query: {query} ---")

        data = search_sold_items(query)
        time.sleep(2)

        if not data:
            continue

        try:
            items = data["findCompletedItemsResponse"][0]["searchResult"][0].get("item", [])
        except:
            continue

        for item in items:
            item_id = item["itemId"][0]

            if item_id not in saved_products:
                title = item["title"][0]
                price = item["sellingStatus"][0]["currentPrice"][0]["__value__"]
                currency = item["sellingStatus"][0]["currentPrice"][0]["@currencyId"]
                url = item["viewItemURL"][0]

                new_products[item_id] = {
                    "title": title,
                    "price": price,
                    "currency": currency,
                    "url": url
                }

    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        save_products(new_products)
        print("Inizializzazione completata.")
        return

    if new_products:
        message = "🔥 NUOVI VENDUTI 🔥\n\n"
        for item in new_products.values():
            message += f"{item['title']}\n💰 {item['price']} {item['currency']}\n{item['url']}\n\n"

        send_telegram(message)

        saved_products.update(new_products)
        save_products(saved_products)
        print("Nuovi venduti notificati.")
    else:
        print("Nessun nuovo venduto.")


if __name__ == "__main__":
    main()