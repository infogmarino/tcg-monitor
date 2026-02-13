import os
import requests
import json
from datetime import datetime

# ==============================
# CONFIG
# ==============================

SEARCH_TERMS = [
    "Charizard PSA 10",
    "Pikachu PSA 10",
    "Umbreon PSA 10",
    "Gengar PSA 10",
    "Eevee PSA 10",
    "Snorlax PSA 10",
    "Celebrations PSA 10",
    "Pokemon JP PSA 10",
    "Chinese Pokemon PSA 10"
]

MAX_RESULTS = 30  # quanti venduti prende ogni volta

EBAY_APP_ID = os.environ.get("EBAY_APP_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ==============================
# TELEGRAM
# ==============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message[:4000]  # limite Telegram
    }

    r = requests.post(url, data=payload)

    try:
        print("Risposta Telegram:", r.json())
    except:
        print("Errore risposta Telegram")

# ==============================
# EBAY SOLD SEARCH (Finding API)
# ==============================

def search_ebay_sold(query):
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
        "paginationInput.entriesPerPage": str(MAX_RESULTS)
    }

    r = requests.get(url, params=params)
    data = r.json()

    try:
        items = data["findCompletedItemsResponse"][0]["searchResult"][0].get("item", [])
    except:
        items = []

    return items

# ==============================
# MAIN LOGIC
# ==============================

def check_ebay():

    print("Controllo venduti:", datetime.utcnow())

    # Carica ID salvati
    try:
        with open("products.json", "r") as f:
            old_ids = set(json.load(f))
    except:
        old_ids = set()

    new_ids = set()
    new_messages = []

    # PRIMA ESECUZIONE
    first_run = len(old_ids) == 0

    for term in SEARCH_TERMS:

        items = search_ebay_sold(term)

        for item in items:

            item_id = item["itemId"][0]

            new_ids.add(item_id)

            if not first_run and item_id not in old_ids:

                title = item["title"][0]
                price = item["sellingStatus"][0]["currentPrice"][0]["__value__"]
                link = item["viewItemURL"][0]

                msg = (
                    f"🔥 NUOVO VENDUTO\n"
                    f"{title}\n"
                    f"💰 €{price}\n"
                    f"{link}\n"
                )

                new_messages.append(msg)

    # Prima esecuzione → solo inizializza
    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
    else:
        if new_messages:
            final_message = "\n\n".join(new_messages)
            send_telegram(final_message)
            print("Notifica inviata!")
        else:
            print("Nessun nuovo venduto.")

    # Salva ID aggiornati
    all_ids = old_ids.union(new_ids)

    with open("products.json", "w") as f:
        json.dump(list(all_ids), f)

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    check_ebay()