import requests
import os
import json
from datetime import datetime

# ===============================
# CONFIG
# ===============================

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

MAX_RESULTS = 20
PRODUCTS_FILE = "products.json"

EBAY_TOKEN = os.getenv("EBAY_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ===============================
# TELEGRAM
# ===============================

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram non configurato.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # Telegram max 4096 caratteri
    if len(message) > 4000:
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    else:
        chunks = [message]

    for chunk in chunks:
        response = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": chunk
        })
        print("Risposta Telegram:", response.text)


# ===============================
# EBAY SEARCH
# ===============================

def search_ebay(query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {EBAY_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {
        "q": query,
        "filter": "soldItems",
        "limit": MAX_RESULTS,
        "sort": "-price"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore eBay:", response.status_code)
        print(response.text)
        return {}

    return response.json()


# ===============================
# MAIN LOGIC
# ===============================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    if not EBAY_TOKEN:
        print("EBAY_TOKEN mancante.")
        return

    # Carica vecchi ID
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r") as f:
            try:
                old_ids = set(json.load(f))
            except:
                old_ids = set()
    else:
        old_ids = set()

    new_ids = set()
    message = ""

    first_run = len(old_ids) == 0

    for term in SEARCH_TERMS:
        results = search_ebay(term)

        if "itemSummaries" not in results:
            continue

        for item in results["itemSummaries"]:
            item_id = item.get("itemId")
            title = item.get("title")
            price = item.get("price", {}).get("value")
            link = item.get("itemWebUrl")

            if not item_id:
                continue

            new_ids.add(item_id)

            # Se prima esecuzione → salva ma non notificare
            if first_run:
                continue

            # Se nuovo venduto
            if item_id not in old_ids:
                message += (
                    f"🔥 NUOVO VENDUTO\n"
                    f"{title}\n"
                    f"💰 €{price}\n"
                    f"{link}\n\n"
                )

    # Prima esecuzione: solo inizializza
    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        with open(PRODUCTS_FILE, "w") as f:
            json.dump(list(new_ids), f)
        print("Inizializzazione completata.")
        return

    # Se ci sono nuovi venduti
    if message:
        send_telegram(message)
        print("Notifica inviata!")
    else:
        print("Nessun nuovo venduto.")

    # Aggiorna file
    all_ids = old_ids.union(new_ids)
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(list(all_ids), f)


# ===============================
# RUN
# ===============================

if __name__ == "__main__":
    check_ebay()