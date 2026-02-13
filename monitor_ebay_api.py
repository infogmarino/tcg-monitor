import requests
import json
import os
from datetime import datetime

# =========================
# CONFIG
# =========================

SEARCH_TERMS = [
    "Charizard PSA 10",
    "Pikachu PSA 10",
    "Chinese PSA 10",
    "Pokemon JP PSA 10",
    "Umbreon PSA 10",
    "Gengar PSA 10",
    "Celebrations PSA 10",
    "Eevee PSA 10",
    "Snorlax PSA 10"
]

EBAY_CLIENT_ID = os.environ.get("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

PRODUCTS_FILE = "products.json"
INITIAL_LOAD_LIMIT = 30
SEARCH_LIMIT = 20

# =========================
# EBAY TOKEN AUTO GENERATION
# =========================

def get_ebay_token():
    url = "https://api.ebay.com/identity/v1/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET)
    )

    if response.status_code != 200:
        print("Errore generazione token:", response.text)
        return None

    return response.json().get("access_token")

# =========================
# EBAY SEARCH
# =========================

def search_ebay(query, token):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "q": query,
        "filter": "soldItems",
        "limit": SEARCH_LIMIT
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore ricerca:", response.status_code, response.text)
        return []

    data = response.json()
    return data.get("itemSummaries", [])

# =========================
# TELEGRAM
# =========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # Telegram max 4096 caratteri
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]

    for chunk in chunks:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": chunk
        })

# =========================
# MAIN
# =========================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    token = get_ebay_token()
    if not token:
        print("Token non generato.")
        return

    # Carica vecchi ID
    try:
        with open(PRODUCTS_FILE, "r") as f:
            old_ids = set(json.load(f))
    except:
        old_ids = set()

    new_ids = set()
    message = ""

    for term in SEARCH_TERMS:
        items = search_ebay(term, token)

        for item in items:
            item_id = item.get("itemId")
            if not item_id:
                continue

            new_ids.add(item_id)

            if item_id not in old_ids:
                title = item.get("title", "No title")
                price = item.get("price", {}).get("value", "N/A")
                link = item.get("itemWebUrl", "")

                message += (
                    f"🔥 NUOVO VENDUTO\n"
                    f"{title}\n"
                    f"💰 €{price}\n"
                    f"{link}\n\n"
                )

    # PRIMA ESECUZIONE
    if not old_ids:
        print("Prima esecuzione: inizializzo senza notificare.")
        new_ids = set(list(new_ids)[:INITIAL_LOAD_LIMIT])

    else:
        if message:
            send_telegram(message)
            print("Notifica inviata!")

    # Salva ID
    all_ids = old_ids.union(new_ids)
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(list(all_ids), f)

    print("Operazione completata.")

# =========================

if __name__ == "__main__":
    check_ebay()