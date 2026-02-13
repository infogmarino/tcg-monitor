import os
import requests
from datetime import datetime

EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
EBAY_TOKEN = os.getenv("EBAY_TOKEN")

QUERIES = [
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

    if response.status_code != 200:
        print("Errore generazione token:", response.text)
        return None

    return response.json().get("access_token")


def search_sold_items(token, query):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": query,
        "filter": "soldItemsOnly:true",
        "limit": 10
    }

    response = requests.get(url, headers=headers, params=params)

    print(f"\n--- Query: {query} ---")
    print("Status code:", response.status_code)

    if response.status_code != 200:
        print("Errore risposta:", response.text)
        return

    data = response.json()
    total = data.get("total", 0)
    print("Totale risultati trovati:", total)

    items = data.get("itemSummaries", [])

    for item in items[:3]:
        print(" -", item.get("title"))


def main():
    print("Test venduti:", datetime.now())

    if not EBAY_APP_ID or not EBAY_CERT_ID:
        print("Chiavi eBay mancanti.")
        return

    token = get_access_token()

    if not token:
        print("Token non generato.")
        return

    print("Token generato correttamente.")

    for query in QUERIES:
        search_sold_items(token, query)


if __name__ == "__main__":
    main()