import os
import requests
import base64
from datetime import datetime

# =========================
# CONFIG
# =========================

CLIENT_ID = os.environ.get("EBAY_APP_ID")
CLIENT_SECRET = os.environ.get("EBAY_CERT_ID")

SEARCH_TERMS = [
    "Charizard PSA 10",
    "Magikarp PSA 10",
    "Eevee PSA 10",
    "Mew PSA 10",
    "Umbreon PSA 10",
    "Chinese PSA 10",
    "Pokemon JP PSA 10",
    "Snorlax PSA 10",
    "Pikachu PSA 10"
]

# =========================
# TOKEN
# =========================

def get_access_token():
    url = "https://api.ebay.com/identity/v1/oauth2/token"

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()

    if "access_token" not in response_json:
        print("ERRORE TOKEN:")
        print(response_json)
        return None

    return response_json["access_token"]

# =========================
# EBAY SEARCH
# =========================

def search_ebay(term, token):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "q": term,
        "filter": "soldItemsOnly:true",
        "limit": 10,
        "sort": "newlyListed"
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()

# =========================
# MAIN
# =========================

def check_ebay():
    print("Monitor eBay avviato...")
    token = get_access_token()

    if not token:
        print("Token non ottenuto. Stop.")
        return

    for term in SEARCH_TERMS:
        print(f"\n🔎 Controllo: {term}")
        results = search_ebay(term, token)

        if "itemSummaries" in results:
            for item in results["itemSummaries"]:
                title = item.get("title")
                price = item.get("price", {}).get("value")
                print(f"- {title} | €{price}")
        else:
            print("Nessun risultato.")

    print("\nControllo completato:", datetime.now())

# =========================

if __name__ == "__main__":
    check_ebay()
