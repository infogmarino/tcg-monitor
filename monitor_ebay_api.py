import os
import requests
import json
from datetime import datetime

# ==========================
# CONFIG
# ==========================

EBAY_TOKEN = os.getenv("EBAY_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

MAX_INIT_ITEMS = 30
PRODUCTS_FILE = "products.json"

# ==========================
# UTILS
# ==========================

def load_saved_ids():
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

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # Telegram limite 4096 caratteri → spezzettiamo a 4000
    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]

        payload = {
            "chat_id": CHAT_ID,
            "text": chunk
        }

        response = requests.post(url, data=payload)
        print("Telegram:", response.text)

# ==========================
# EBAY REQUEST
# ==========================

def search_ebay(term):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {EBAY_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {
        "q": term,
        "filter": "soldItemsOnly:true",
        "sort": "-price",
        "limit": 20
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("STATUS CODE:", response.status_code)
        print("RISPOSTA RAW:", response.text)
        return []

    data = response.json()
    return data.get("itemSummaries", [])

# ==========================
# MAIN
# ==========================

def main():
    print("Controllo venduti:", datetime.now())

    if not EBAY_TOKEN:
        print("EBAY_TOKEN mancante.")
        return

    saved_ids = load_saved_ids()
    new_ids = set(saved_ids)
    first_run = len(saved_ids) == 0

    new_messages = []

    for term in SEARCH_TERMS:
        items = search_ebay(term)

        for item in items:
            item_id = item.get("itemId")

            if not item_id:
                continue

            if item_id not in saved_ids:
                new_ids.add(item_id)

                if not first_run:
                    title = item.get("title", "No title")
                    price = item.get("price", {}).get("value", "N/A")
                    currency = item.get("price", {}).get("currency", "")
                    link = item.get("itemWebUrl", "")

                    message = (
                        f"🔥 VENDUTO TROVATO\n\n"
                        f"{title}\n"
                        f"{price} {currency}\n"
                        f"{link}\n"
                    )

                    new_messages.append(message)

    # Prima esecuzione → salva solo ultimi 30 e basta
    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        save_ids(list(new_ids)[:MAX_INIT_ITEMS])
        print("Inizializzazione completata.")
        return

    # Invia notifiche
    if new_messages:
        final_text = "\n\n".join(new_messages)
        send_telegram_message(final_text)

    save_ids(new_ids)
    print("Controllo completato.")

if __name__ == "__main__":
    main()