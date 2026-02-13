import requests
import os
import json
import base64
from datetime import datetime

# =============================
# CONFIG
# =============================

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

MAX_STORED_PER_QUERY = 6
PRODUCTS_FILE = "products.json"

# =============================
# EBAY TOKEN AUTO GENERATION
# =============================

def get_ebay_token():
    app_id = os.getenv("EBAY_APP_ID")
    cert_id = os.getenv("EBAY_CERT_ID")

    credentials = f"{app_id}:{cert_id}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers=headers,
        data=data
    )

    if response.status_code != 200:
        print("Errore generazione token:")
        print(response.text)
        return None

    return response.json()["access_token"]

# =============================
# LOAD / SAVE PRODUCTS
# =============================

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return {}
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)

# =============================
# TELEGRAM
# =============================

def send_telegram(message):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    requests.post(url, data={
        "chat_id": chat_id,
        "text": message
    })

# =============================
# MAIN
# =============================

def main():
    print("Controllo venduti:", datetime.now())

    token = get_ebay_token()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}"
    }

    stored_products = load_products()
    new_sold_found = 0

    for query in QUERIES:
        print(f"--- Query: {query} ---")

        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

        params = {
            "q": query,
            "filter": "soldItemsOnly:true",
            "limit": 10
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print("Errore eBay:", response.status_code)
            print(response.text)
            continue

        data = response.json()
        items = data.get("itemSummaries", [])

        if query not in stored_products:
            stored_products[query] = []

        existing_ids = stored_products[query]

        for item in items:
            item_id = item["itemId"]

            if item_id not in existing_ids:
                new_sold_found += 1

                title = item["title"]
                price = item["price"]["value"]
                currency = item["price"]["currency"]
                link = item["itemWebUrl"]

                message = (
                    f"🟢 NUOVO VENDUTO\n\n"
                    f"{title}\n"
                    f"{price} {currency}\n"
                    f"{link}"
                )

                send_telegram(message)

                stored_products[query].insert(0, item_id)

        # Manteniamo solo gli ultimi 6
        stored_products[query] = stored_products[query][:MAX_STORED_PER_QUERY]

    save_products(stored_products)

    if new_sold_found == 0:
        print("Nessun nuovo venduto.")
    else:
        print("Nuovi venduti trovati:", new_sold_found)

# =============================

if __name__ == "__main__":
    main()