import requests
import json
import os
import base64
from datetime import datetime

# ==============================
# CONFIG
# ==============================

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

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PRODUCTS_FILE = "products.json"


# ==============================
# TELEGRAM
# ==============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=payload)
    print("Risposta Telegram:", response.text)


# ==============================
# EBAY TOKEN
# ==============================

def get_ebay_token():
    url = "https://api.ebay.com/identity/v1/oauth2/token"

    credentials = f"{EBAY_APP_ID}:{EBAY_CERT_ID}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print("Errore token:", response.text)
        return None

    return response.json().get("access_token")


# ==============================
# EBAY SEARCH
# ==============================

def search_ebay(query, token):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "q": query,
        "filter": "soldItems",
        "limit": "20",
        "sort": "-endTime"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore ricerca:", response.text)
        return {}

    return response.json()


# ==============================
# MAIN LOGIC
# ==============================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    token = get_ebay_token()
    if not token:
        print("Token non valido.")
        return

    # Carica ID salvati
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r") as f:
            try:
                old_ids = set(json.load(f))
            except:
                old_ids = set()
    else:
        old_ids = set()

    new_ids = set()
    first_run = len(old_ids) == 0
    message = ""

    for term in SEARCH_TERMS:
        results = search_ebay(term, token)

        if "itemSummaries" in results:
            for item in results["itemSummaries"]:
                item_id = item.get("itemId")

                if not item_id:
                    continue

                if first_run:
                    new_ids.add(item_id)
                    continue

                if item_id not in old_ids:
                    title = item.get("title", "No title")
                    price = item.get("price", {}).get("value", "N/A")
                    link = item.get("itemWebUrl", "")

                    message += (
                        f"🔥 <b>NUOVO VENDUTO</b>\n"
                        f"{title}\n"
                        f"💰 {price} €\n"
                        f"{link}\n\n"
                    )

                    new_ids.add(item_id)

    # Prima esecuzione: solo salva
    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")
        with open(PRODUCTS_FILE, "w") as f:
            json.dump(list(new_ids), f)
        print("Inizializzazione completata.")
        return

    # Invia solo se ci sono nuovi venduti
    if message:
        send_telegram(message)
        print("Notifica inviata!")

    # Salva ID aggiornati
    all_ids = old_ids.union(new_ids)
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(list(all_ids), f)


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    check_ebay()