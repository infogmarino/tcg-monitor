import requests
from bs4 import BeautifulSoup
import json
import os

CATEGORIES = {
    # WINLEOO
    "Winleoo - Dragon Ball": "https://winleoo.com/product-category/prodotti-fisici/trading-cards/dragon-ball-trading-cards/",
    "Winleoo - One Piece": "https://winleoo.com/product-category/prodotti-fisici/trading-cards/one-piece-trading-cards/",
    "Winleoo - Pokemon": "https://winleoo.com/product-category/prodotti-fisici/trading-cards/pokemon-trading-cards/",

    # LUDOSFERA
    "Ludosfera - One Piece": "https://www.ludosfera.it/collections/one-piece-card-game",
    "Ludosfera - Dragon Ball Fusion": "https://www.ludosfera.it/collections/dragon-ball-fusion-card-game",
    "Ludosfera - Pokemon": "https://www.ludosfera.it/collections/pokemon"
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATA_FILE = "products.json"

headers = {"User-Agent": "Mozilla/5.0"}

def send_telegram(text):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text}
    )

def get_products_winleoo(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("ul.products li a.woocommerce-LoopProduct-link")
    return {i["href"]: i.text.strip() for i in items}

def get_products_shopify(url):
    r = requests.get(url + ".json", headers=headers)
    data = r.json()
    products = {}
    for product in data.get("products", []):
        link = f"{url.replace('/collections', '/products')}/{product['handle']}"
        products[link] = product["title"]
    return products

def load_old():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_current(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

old = load_old()
current = {}
message = ""

for name, url in CATEGORIES.items():
    try:
        if "winleoo" in url:
            products = get_products_winleoo(url)
        else:
            products = get_products_shopify(url)

        current[name] = products
        old_products = old.get(name, {})
        new_items = set(products.keys()) - set(old_products.keys())

        if new_items:
            message += f"🔥 Nuovi prodotti {name}:\n\n"
            for link in new_items:
                message += f"{products[link]}\n{link}\n\n"

    except Exception as e:
        print(f"Errore su {name}: {e}")

message += "🧪 PRODOTTO TEST SIMULATO\nhttps://test-link.com\n\n"

print("MESSAGGIO FINALE:")
print(message)

send_telegram("TEST FORZATO")

save_current(current)
