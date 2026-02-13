import requests
import os
import json
import time

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
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

FINDING_API_URL = "https://svcs.ebay.com/services/search/FindingService/v1"


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text[:4000]
    }
    requests.post(url, data=payload)


def load_products():
    try:
        with open("products.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_products(products):
    with open("products.json", "w") as f:
        json.dump(products, f, indent=2)


def search_sold_items(query):
    headers = {
        "X-EBAY-SOA-OPERATION-NAME": "findCompletedItems",
        "X-EBAY-SOA-SERVICE-VERSION": "1.13.0",
        "X-EBAY-SOA-SECURITY-APPNAME": EBAY_APP_ID,
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "JSON"
    }

    params = {
        "keywords": query,
        "itemFilter(0).name": "SoldItemsOnly",
        "itemFilter(0).value": "true",
        "sortOrder": "EndTimeSoonest"
    }

    response = requests.get(FINDING_API_URL, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore eBay:", response.status_code)
        return []

    data = response.json()

    try:
        items = data["findCompletedItemsResponse"][0]["searchResult"][0]["item"]
    except:
        return []

    results = []

    for item in items[:20]:
        item_id = item["itemId"][0]
        title = item["title"][0]
        price = item["sellingStatus"][0]["currentPrice"][0]["__value__"]
        currency = item["sellingStatus"][0]["currentPrice"][0]["@currencyId"]
        url = item["viewItemURL"][0]

        results.append({
            "id": item_id,
            "title": title,
            "price": price,
            "currency": currency,
            "url": url
        })

    return results


def main():
    print("Controllo venduti...")

    if not EBAY_APP_ID:
        print("Chiavi eBay mancanti.")
        return

    products = load_products()

    first_run = len(products) == 0
    new_products = {}

    for query in SEARCH_QUERIES:
        print(f"--- Query: {query} ---")

        sold_items = search_sold_items(query)

        for item in sold_items:
            item_id = item["id"]

            if item_id not in products:
                new_products[item_id] = item

                if not first_run:
                    message = (
                        f"🔥 NUOVO VENDUTO 🔥\n\n"
                        f"{item['title']}\n"
                        f"{item['price']} {item['currency']}\n\n"
                        f"{item['url']}"
                    )
                    send_telegram_message(message)
                    time.sleep(1)

    products.update(new_products)
    save_products(products)

    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
    else:
        if len(new_products) == 0:
            print("Nessun nuovo venduto.")
        else:
            print(f"{len(new_products)} nuovi venduti notificati.")


if __name__ == "__main__":
    main()