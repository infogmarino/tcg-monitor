import requests
import os
import json
from datetime import datetime

# =========================
# CONFIG
# =========================

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

MAX_RESULTS = 30
PRODUCTS_FILE = "products.json"

EBAY_APP_ID = os.environ.get("EBAY_APP_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# =========================
# TELEGRAM
# =========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    r = requests.post(url, data=payload)

    print("Risposta Telegram:", r.text)


# =========================
# EBAY FINDING API
# =========================

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

    print("STATUS CODE:", r.status_code)
    print("RISPOSTA RAW:", r.text[:400])

    if r.status_code != 200:
        return []

    try:
        data = r.json()
        items = data["findCompletedItemsResponse"][0]["searchResult"][0].get("item", [])
        print(f"Trovati {len(items)} risultati per:", query)
        return items
    except Exception as e:
        print("Errore parsing:", e)
        return []


# =========================
# MAIN LOGIC
# =========================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    # Carica ID già salvati
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "w") as f:
            json.dump([], f)

    with open(PRODUCTS_FILE, "r") as f:
        try:
            old_ids = set(json.load(f))
        except:
            old_ids = set()

    first_run = len(old_ids) == 0
    new_ids = set()
    message = ""

    for term in SEARCH_TERMS:
        items = search_ebay_sold(term)

        for item in items:
            item_id = item.get("itemId", [None])[0]
            title = item.get("title", [""])[0]
            price = item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__", "")
            link = item.get("viewItemURL", [""])[0]

            if not item_id:
                continue

            # PRIMA ESECUZIONE → salva tutto senza notificare
            if first_run:
                new_ids.add(item_id)
                continue

            # NUOVI VENDUTI
            if item_id not in old_ids:
                message += (
                    f"🔥 NUOVO VENDUTO\n"
                    f"{title}\n"
                    f"💰 €{price}\n"
                    f"{link}\n\n"
                )
                new_ids.add(item_id)

    # Prima esecuzione: inizializza
    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")

        with open(PRODUCTS_FILE, "w") as f:
            json.dump(list(new_ids), f)

        print("Inizializzazione completata.")
        return

    # Se ci sono nuovi venduti → Telegram
    if message:
        send_telegram(message)
        print("Notifica inviata!")
    else:
        print("Nessun nuovo venduto.")

    # Salva ID aggiornati
    all_ids = old_ids.union(new_ids)

    with open(PRODUCTS_FILE, "w") as f:
        json.dump(list(all_ids), f)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    check_ebay()