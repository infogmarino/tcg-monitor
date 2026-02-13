import requests
import os
import json
from datetime import datetime

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


def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return {}
    with open(PRODUCTS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=4)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message[:3500]
    }
    requests.post(url, data=payload)


def search_sold(query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {EBAY_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {
        "q": query,
        "filter": "soldItems",
        "sort": "-endTime",
        "limit": "20"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore eBay:", response.text)
        return []

    data = response.json()
    return data.get("itemSummaries", [])


def main():
    print("Controllo venduti:", datetime.now())

    if not EBAY_TOKEN or not BOT_TOKEN or not CHAT_ID:
        print("Variabili ambiente mancanti.")
        return

    products = load_products()
    first_run = len(products) == 0

    new_products = {}

    for query in QUERIES:
        items = search_sold(query)

        for item in items:
            item_id = item["itemId"]

            if item_id not in products:
                new_products[item_id] = {
                    "title": item["title"],
                    "price": item["price"]["value"],
                    "currency": item["price"]["currency"],
                    "url": item["itemWebUrl"]
                }

    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        products.update(new_products)
        save_products(products)
        print("Inizializzazione completata.")
        return

    for item_id, data in new_products.items():
        message = (
            f"🔥 NUOVA VENDITA!\n\n"
            f"{data['title']}\n"
            f"{data['price']} {data['currency']}\n"
            f"{data['url']}"
        )
        send_telegram(message)

    if new_products:
        products.update(new_products)
        save_products(products)
        print("Nuove vendite salvate.")
    else:
        print("Nessuna nuova vendita.")


if __name__ == "__main__":
    main()