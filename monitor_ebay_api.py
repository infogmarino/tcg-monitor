import requests
import json
import os
from datetime import datetime

# ==============================
# CONFIG
# ==============================

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SEARCH_TERMS = [
    "Charizard PSA 10",
    "Pikachu PSA 10",
    "Chinese PSA 10 Pokemon",
    "Pokemon JP PSA 10",
    "Umbreon PSA 10",
    "Gengar PSA 10",
    "Celebrations PSA 10",
    "Eevee PSA 10",
    "Snorlax PSA 10"
]

MAX_RESULTS_PER_SEARCH = 20
MAX_NOTIFICATIONS_PER_RUN = 10

PRODUCTS_FILE = "products.json"

# ==============================
# TELEGRAM
# ==============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    MAX_LENGTH = 4000

    for i in range(0, len(message), MAX_LENGTH):
        chunk = message[i:i + MAX_LENGTH]

        payload = {
            "chat_id": CHAT_ID,
            "text": chunk
        }

        response = requests.post(url, data=payload)
        print("Telegram:", response.text)

# ==============================
# EBAY SEARCH
# ==============================

def search_ebay(query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {EBAY_APP_ID}",
        "Content-Type": "application/json"
    }

    params = {
        "q": query,
        "filter": "soldItems",
        "limit": MAX_RESULTS_PER_SEARCH,
        "sort": "-price"
    }

    response = requests.get(url, headers=headers, params=params)

    print("STATUS CODE:", response.status_code)

    if response.status_code != 200:
        print("RISPOSTA RAW:", response.text)
        return {}

    return response.json()

# ==============================
# MAIN LOGIC
# ==============================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    # Carica ID salvati
    try:
        with open(PRODUCTS_FILE, "r") as f:
            old_ids = set(json.load(f))
    except:
        old_ids = set()

    first_run = len(old_ids) == 0
    new_ids = set()
    message = ""
    notifications_sent = 0

    for term in SEARCH_TERMS:
        results = search_ebay(term)

        if "itemSummaries" not in results:
            continue

        for item in results["itemSummaries"]:
            item_id = item.get("itemId")

            if not item_id:
                continue

            new_ids.add(item_id)

            if first_run:
                continue

            if item_id not in old_ids and notifications_sent < MAX_NOTIFICATIONS_PER_RUN:
                title = item.get("title", "No title")
                price = item.get("price", {}).get("value", "N/A")
                link = item.get("itemWebUrl", "")

                message += (
                    f"🔥 NUOVO VENDUTO\n"
                    f"{title}\n"
                    f"💰 €{price}\n"
                    f"{link}\n\n"
                )

                notifications_sent += 1

    # Prima esecuzione → salva senza notificare
    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        with open(PRODUCTS_FILE, "w") as f:
            json.dump(list(new_ids), f)
        print("Inizializzazione completata.")
        return

    # Invia notifiche
    if message:
        send_telegram(message)
        print("Notifiche inviate!")
    else:
        print("Nessun nuovo venduto.")

    # Salva ID aggiornati
    all_ids = old_ids.union(new_ids)

    with open(PRODUCTS_FILE, "w") as f:
        json.dump(list(all_ids), f)

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    check_ebay()