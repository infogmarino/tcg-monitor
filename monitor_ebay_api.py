import requests
import json
import os
from datetime import datetime

# =========================
# CONFIG
# =========================

EBAY_TOKEN = os.getenv("EBAY_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SEARCH_QUERIES = [
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

PRODUCTS_FILE = "products.json"
MAX_RESULTS_PER_QUERY = 10


# =========================
# TELEGRAM
# =========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message[:4000]  # Evita errore text too long
    }

    response = requests.post(url, data=payload)
    print("Telegram:", response.text)


# =========================
# EBAY SEARCH
# =========================

def search_ebay(query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {EBAY_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {
        "q": query,
        "filter": "soldItems",
        "sort": "-price",
        "limit": MAX_RESULTS_PER_QUERY
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("STATUS CODE:", response.status_code)
        print("RISPOSTA RAW:", response.text)
        return {}

    return response.json()


# =========================
# LOAD / SAVE IDS
# =========================

def load_ids():
    if not os.path.exists(PRODUCTS_FILE):
        return set()

    with open(PRODUCTS_FILE, "r") as f:
        try:
            data = json.load(f)
            return set(data)
        except:
            return set()


def save_ids(ids):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(list(ids), f)


# =========================
# MAIN CHECK
# =========================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    old_ids = load_ids()
    new_ids = set()
    messages = []

    for query in SEARCH_QUERIES:
        data = search_ebay(query)

        items = data.get("itemSummaries", [])
        for item in items:
            item_id = item.get("itemId")

            if item_id not in old_ids:
                title = item.get("title", "No title")
                price = item.get("price", {}).get("value", "N/A")
                link = item.get("itemWebUrl", "")

                msg = (
                    f"🔥 NUOVO VENDUTO\n\n"
                    f"{title}\n"
                    f"💰 €{price}\n"
                    f"{link}\n"
                )

                messages.append(msg)
                new_ids.add(item_id)

    # PRIMA ESECUZIONE → salva senza notificare
    if not old_ids:
        print("Prima esecuzione: inizializzo senza notificare.")
        save_ids(new_ids)
        print("Inizializzazione completata.")
        return

    # Invia notifiche solo nuovi
    if messages:
        for msg in messages:
            send_telegram(msg)

        print("Notifiche inviate.")
    else:
        print("Nessun nuovo venduto.")

    # Aggiorna file
    all_ids = old_ids.union(new_ids)
    save_ids(all_ids)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    check_ebay()