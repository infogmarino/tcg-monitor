import os
import requests
import json
from datetime import datetime

# =========================
# CONFIG
# =========================

SEARCH_TERMS = [
    "Charizard PSA 10",
    "Lugia PSA 10",
]

EBAY_APP_ID = os.environ.get("EBAY_APP_ID")
EBAY_CERT_ID = os.environ.get("EBAY_CERT_ID")

# =========================
# TELEGRAM
# =========================

def send_telegram(message):
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not bot_token or not chat_id:
        print("Telegram non configurato.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": message
    })

    print("Risposta Telegram:", response.text)


# =========================
# EBAY TOKEN
# =========================

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
        auth=(EBAY_APP_ID, EBAY_CERT_ID)
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Errore token:", response.status_code, response.text)
        return None


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
        "filter": "soldItems:true",
        "limit": "20"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Errore ricerca:", response.status_code, response.text)
        return {}


# =========================
# MAIN
# =========================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    token = get_access_token()
    if not token:
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

    if message:
        send_telegram(message)
        print("Notifica inviata!")
    else:
        print("Nessun nuovo venduto.")

    # Salva ID aggiornati
    all_ids = old_ids.union(new_ids)

    with open("products.json", "w") as f:
        json.dump(list(all_ids), f)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    check_ebay()