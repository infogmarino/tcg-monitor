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

def get_sold_items(query):
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    
    params = {
        "OPERATION-NAME": "findCompletedItems",
        "SERVICE-VERSION": "1.13.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "REST-PAYLOAD": "",
        "keywords": query,
        "itemFilter(0).name": "SoldItemsOnly",
        "itemFilter(0).value": "true",
        "paginationInput.entriesPerPage": "5"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Errore eBay: {response.status_code}")
        return []

    data = response.json()

    try:
        items = data["findCompletedItemsResponse"][0]["searchResult"][0].get("item", [])
        return items
    except:
        return []

def load_products():
    if not os.path.exists("products.json"):
        return {}
    with open("products.json", "r") as f:
        return json.load(f)

def save_products(products):
    with open("products.json", "w") as f:
        json.dump(products, f, indent=2)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

def main():
    print("Controllo venduti:", datetime.now())

    products = load_products()
    new_products = {}

    for query in SEARCH_TERMS:
        print(f"--- Query: {query} ---")

        items = get_sold_items(query)

        for item in items:
            item_id = item["itemId"][0]

            if item_id not in products:
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

        time.sleep(2)  # 🛑 pausa anti rate limit

    if not products:
        print("Prima esecuzione: inizializzo senza notificare.")
        save_products(new_products)
        return

    if new_products:
        for item_id, info in new_products.items():
            message = f"🔥 NUOVO VENDUTO!\n\n{info['title']}\n💰 {info['price']} {info['currency']}\n{info['url']}"
            send_telegram(message)

        products.update(new_products)
        save_products(products)
    else:
        print("Nessun nuovo venduto.")

if __name__ == "__main__":
    main()