import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

# ==============================
# CONFIG
# ==============================

SEARCH_TERMS = [
    "charizard psa 10",
    "magikarp psa 10",
    "eevee psa 10",
    "mew psa 10",
    "umbreon psa 10",
    "snorlax psa 10",
    "pikachu psa 10"
]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATA_FILE = "ebay_sold.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ==============================
# TELEGRAM
# ==============================

def send_telegram(text):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text}
    )

# ==============================
# STORAGE
# ==============================

def load_old_ids():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return set(json.load(f))
    return set()

def save_ids(ids):
    with open(DATA_FILE, "w") as f:
        json.dump(list(ids), f)

# ==============================
# EBAY
# ==============================

def extract_item_id(link):
    match = re.search(r"/itm/(\d+)", link)
    return match.group(1) if match else None

def get_recent_sold(term):
    url = f"https://www.ebay.it/sch/i.html?_nkw={term.replace(' ', '+')}&LH_Sold=1&LH_Complete=1&rt=nc"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select(".s-item")

    results = []

    for item in items[:5]:
        title_tag = item.select_one(".s-item__title")
        price_tag = item.select_one(".s-item__price")
        link_tag = item.select_one("a.s-item__link")

        if not title_tag or not price_tag or not link_tag:
            continue

        link = link_tag["href"]
        item_id = extract_item_id(link)

        if not item_id:
            continue

        results.append({
            "id": item_id,
            "title": title_tag.text.strip(),
            "price": price_tag.text.strip(),
            "link": link
        })

    return results

# ==============================
# MAIN
# ==============================

def check_ebay():
    print("Controllo venduti:", datetime.now())

    old_ids = load_old_ids()
    new_ids = set()
    message = ""

    for term in SEARCH_TERMS:
        items = get_recent_sold(term)

        for item in items:
            if item["id"] not in old_ids:
                message += (
                    f"🔥 NUOVO VENDUTO\n"
                    f"{item['title']}\n"
                    f"💰 {item['price']}\n"
                    f"{item['link']}\n\n"
                )
                new_ids.add(item["id"])

    if message:
        send_telegram(message)

    all_ids = old_ids.union(new_ids)
    save_ids(all_ids)


if __name__ == "__main__":
    check_ebay()
