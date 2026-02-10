import requests
import os
import json

KEYWORDS = [
    "Charizard PSA 10",
    "Umbreon PSA 10",
    "Pikachu PSA 10",
    "Gengar",
    "Mew PSA 10",
    "Mewtwo PSA 10",
    "Celebrations",
    "Snorlax PSA 10",
    "Ho-oh PSA 10",
    "Magikarp PSA 10",
    "Eevee PSA 10",
    "Venusaur PSA 10",
    "Blastoise PSA 10",
    "Moltres PSA 10"
]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DATA_FILE = "ebay_api_sold.json"

def send_telegram(text):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text}
    )

def load_ids():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_ids(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

print("Script pronto - in attesa API eBay...")
