import requests
import os
import json
from datetime import datetime

# ==============================
# CONFIG
# ==============================

SEARCH_TERMS = [
    "Charizard PSA 10",
    "Magikarp PSA 10"
]

EBAY_CLIENT_ID = os.environ.get("EBAY_APP_ID")
EBAY_CLIENT_SECRET = os.environ.get("EBAY_CERT_ID")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ==============================
# TELEGRAM
# ==============================

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram non configurato.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# ==============================
# EBAY AUTH
# ==============================

def get_access_token():
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

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Errore token:", response.text)
        return None

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
        "limit": "20"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Errore eBay:", response.status_code, response.text)
        return {}

    return response.json()

    else:
        print("Errore ricerca:", response.text)
        return {}

# ==============================
# MAIN CHECK
# ==============================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    token = get_access_token()
    if not token:
        print("Token non ottenuto.")
        return

    # Carica ID già notificati
    try:
        with open("products.json", "r") as f:
            old_ids = set(json.load(f))
    except:
        old_ids = set()

    new_ids = set()
    message = ""

    for term in SEARCH_TERMS:
        results = search_ebay(term, token)

        if "itemSummaries" in results:
            for item in results["itemSummaries"]:
                item_id = item.get("itemId")

                if item_id not in old_ids:
                    title = item.get("title")
                    price = item.get("price", {}).get("value")
                    link = item.get("itemWebUrl")

                    message += (
                        f"🔥 NUOVO VENDUTO\n"
                        f"{title}\n"
                        f"💰 €{price}\n"
                        f"{link}\n\n"
                    )

                    new_ids.add(item_id)

    # Invia solo se ci sono nuovi venduti
    if message:
        send_telegram("Test eBay forzato")
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
