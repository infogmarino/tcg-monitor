import os
import requests
import json
from datetime import datetime

# ==========================================
# CARTE DA MONITORARE
# ==========================================

SEARCH_TERMS = [
    "Charizard PSA 10",
    "Pikachu PSA 10",
    "Umbreon PSA 10",
    "Gengar PSA 10",
    "Eevee PSA 10",
    "Snorlax PSA 10",
    "Pokemon Chinese PSA 10",
    "Pokemon Japanese PSA 10",
    "Pokemon Celebrations PSA 10"
]

EBAY_APP_ID = os.environ.get("EBAY_APP_ID")
EBAY_CERT_ID = os.environ.get("EBAY_CERT_ID")

# ==========================================
# TELEGRAM
# ==========================================

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


# ==========================================
# TOKEN EBAY
# ==========================================

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


# ==========================================
# RICERCA EBAY
# ==========================================

def search_ebay(query, token):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_IT"
    }

    params = {
        "q": query,
        "filter": "soldItems:true",
        "sort": "newlyListed",
        "limit": "10"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Errore ricerca:", response.status_code, response.text)
        return {}


# ==========================================
# LOGICA PRINCIPALE
# ==========================================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    token = get_access_token()
    if not token:
        return

    # Carica ID già salvati
    try:
        with open("products.json", "r") as f:
            old_ids = set(json.load(f))
    except:
        old_ids = set()

    first_run = len(old_ids) == 0

    all_found_ids = set()
    new_items = []

    for term in SEARCH_TERMS:
        results = search_ebay(term, token)

        if "itemSummaries" in results:
            for item in results["itemSummaries"]:
                item_id = item.get("itemId")
                title = item.get("title", "").lower()

                # Filtro sicurezza PSA 10 reale
                if "psa 10" not in title:
                    continue

                all_found_ids.add(item_id)

                if item_id not in old_ids:
                    new_items.append(item)

    # ==========================
    # PRIMA ESECUZIONE
    # ==========================
    if first_run:
        print("Prima esecuzione: inizializzo senza notificare.")

        # Salva massimo 30 ID iniziali
        initial_ids = list(all_found_ids)[:30]

        with open("products.json", "w") as f:
            json.dump(initial_ids, f)

        print("Inizializzazione completata.")
        return

    # ==========================
    # RUN NORMALI
    # ==========================

    # Limita massimo 10 notifiche per run
    new_items = new_items[:10]

    message = ""

    for item in new_items:
        item_id = item.get("itemId")
        title = item.get("title")
        price = item.get("price", {}).get("value")
        link = item.get("itemWebUrl")

        message += (
            f"🔥 NUOVO VENDUTO\n"
            f"{title}\n"
            f"💰 €{price}\n"
            f"{link}\n\n"
        )

    if message:
        send_telegram(message)
        print("Notifica inviata!")
    else:
        print("Nessun nuovo venduto.")

    # Aggiorna file con nuovi ID
    updated_ids = old_ids.union({item.get("itemId") for item in new_items})

    with open("products.json", "w") as f:
        json.dump(list(updated_ids), f)


# ==========================================
# AVVIO SCRIPT
# ==========================================

if __name__ == "__main__":
    check_ebay()