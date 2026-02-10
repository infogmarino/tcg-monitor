import requests
from bs4 import BeautifulSoup
import json
import os
import re

EBAY_URL = "https://www.ebay.it/sch/i.html?_nkw=charizard+psa+10&LH_Sold=1&_udlo=40"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATA_FILE = "ebay_sold.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send_telegram(text):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text}
    )

def load_old_ids():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return set(json.load(f))
    return set()

def save_ids(ids):
    with open(DATA_FILE, "w") as f:
        json.dump(list(ids), f)

def extract_item_id(link):
    match = re.search(r"/itm/(\d+)", link)
    return match.group(1) if match else None

def get_recent_sold():
    r = requests.get(EBAY_URL, headers=headers)

print("Status:", r.status_code)
print(r.text[:500])

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

old_ids = load_old_ids()
current_items = get_recent_sold()

new_ids = set()
message = ""

for item in current_items:
    if item["id"] not in old_ids:
        message += f"🔥 Nuovo venduto eBay!\n\n{item['title']}\n💰 {item['price']}\n{item['link']}\n\n"
        new_ids.add(item["id"])

if message:
    send_telegram(message)

all_ids = old_ids.union(new_ids)
save_ids(all_ids)
