import requests
import json
import os
from datetime import datetime

PRODUCTS_FILE = "products.json"

QUERIES = [
    "Charizard psa 10",
    "Pikachu psa 10",
    "Chinese psa 10",
    "Pokemon Jp psa 10",
    "Umbreon psa 10",
    "Gengar psa 10",
    "Celebrations psa 10",
    "Eevee psa 10",
    "Snorlax psa 10",
]


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
        json.dump(products, f, indent=2)


def search_ebay(query):
    url = "https://svcs.ebay.com/services/search/FindingService/v1"

    params = {
        "OPERATION-NAME": "findCompletedItems",
        "SERVICE-VERSION": "1.13.0",
        "SECURITY-APPNAME": os.getenv("EBAY_APP_ID"),
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": query,
        "itemFilter(0).name": "SoldItemsOnly",
        "itemFilter(0).value": "true",
        "paginationInput.entriesPerPage": "20",
        "sortOrder": "EndTimeSoonest"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Errore eBay:", response.status_code)
        print(response.text)
        return []

    data = response.json()

    try:
        return data["findCompletedItemsResponse"][0]["searchResult"][0].get("item", [])
    except:
        return []


def send_telegram_message(text):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not bot_token or not chat_id:
        print("Telegram non configurato.")
        return

    # Limite Telegram 4096 caratteri
    if len(text) > 4000:
        text = text[:4000]

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    requests.post(url, data=payload)


def main():
    print("Controllo venduti:", datetime.now())

    products = load_products()
    first_run = len(products) == 0

    new_products = {}

    for query in QUERIES:
        print(f"--- Query: {query} ---")

        items = search_ebay(query)

        for item in items:
            item_id = item["itemId"][0]

            if item_id in products:
                continue

            title = item["title"][0]
            price_info = item["sellingStatus"][0]["currentPrice"][0]
            price = price_info["__value__"]
            currency = price_info["currencyId"]
            url = item["viewItemURL"][0]

            new_products[item_id] = {
                "title": title,
                "price": price,
                "currency": currency,
                "url": url
            }

    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        products.update(new_products)
        save_products(products)
        print("Inizializzazione completata.")
        return

    if not new_products:
        print("Nessun nuovo venduto.")
        return

    # Notifica Telegram
    message = "<b>Nuovi venduti trovati:</b>\n\n"

    for item in new_products.values():
        message += (
            f"<b>{item['title']}</b>\n"
            f"Prezzo: {item['price']} {item['currency']}\n"
            f"{item['url']}\n\n"
        )

    send_telegram_message(message)

    products.update(new_products)
    save_products(products)

    print("Notifica inviata.")


if __name__ == "__main__":
    main()