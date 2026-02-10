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
    "Ludosfera - Pokemon": "https://www.ludosfera.it/collections/pokemon",

    # DNA CARDS
    "DNA - Dragon Ball": "https://dnacards.it/categoria/prevendita/?show=in_stock&orderby=&filter_category=70&brand=18",
    "DNA - One Piece": "https://dnacards.it/categoria/prevendita/?show=in_stock&orderby=&filter_category=70&brand=48",
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATA_FILE = "products.json"

headers = {"User-Agent": "Mozilla/5.0"}

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN o CHAT_ID mancanti")
        return

    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text},
        timeout=10
    )

def get_products_winleoo(url):
    products = {}
    page = 1

    while True:
        if page == 1:
            page_url = url
        else:
            page_url = url.rstrip("/") + f"/page/{page}/"

        r = requests.get(page_url, headers=headers, timeout=15)

        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("ul.products li a.woocommerce-LoopProduct-link")

        if not items:
            break  # nessun prodotto = fine pagine

        for i in items:
            link = i["href"]
            title = i.text.strip()
            products[link] = title

        page += 1

    return products

def get_products_shopify(url):
    base = url.split("/collections")[0]
    handle = url.split("/collections/")[1]

    api_url = f"{base}/collections/{handle}/products.json"

    r = requests.get(api_url, headers=headers, timeout=15)
    data = r.json()

    products = {}

    for product in data.get("products", []):
        link = f"{base}/products/{product['handle']}"
        products[link] = product["title"]

    return products

def get_products_dnacards(url):
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("ul.products li a.woocommerce-LoopProduct-link")
    return {i["href"]: i.text.strip() for i in items}

def load_old():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_current(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

old = load_old()
print("OLD DATA:", old)

current = {}
message = ""

for name, url in CATEGORIES.items():
    try:
        if "winleoo" in url:
            products = get_products_winleoo(url)
            print(name, "PRODOTTI TROVATI:", len(products))

        elif "dnacards" in url:
            products = get_products_dnacards(url)
            print(name, "PRODOTTI TROVATI:", len(products))

        else:
            products = get_products_shopify(url)
            print(name, "PRODOTTI TROVATI:", len(products))

        current[name] = products
        old_products = old.get(name, {})
        new_items = set(products.keys()) - set(old_products.keys())

        if new_items:
            message += f"🔥 Nuovi prodotti {name}:\n\n"
            for link in new_items:
                message += f"{products[link]}\n{link}\n\n"

    except Exception as e:
        print(f"Errore su {name}: {e}")

if message:
    send_telegram(message)


save_current(current)
