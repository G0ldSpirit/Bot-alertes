import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SLUG = os.getenv("SLUG")
THRESHOLD = float(os.getenv("THRESHOLD", "0.65"))

def get_markets(slug):
    url = f"https://gamma-api.polymarket.com/public-search?q={slug}"
    r = requests.get(url)
    data = r.json()
    markets = []

    if "events" in data:
        for ev in data["events"]:
            if ev.get("slug") == slug:
                for m in ev.get("markets", []):
                    markets.append({
                        "id": m["id"],
                        "question": m.get("question", "Marché")
                    })
    return markets

def get_price(market_id):
    url = f"https://clob.polymarket.com/markets/{market_id}"
    r = requests.get(url)
    data = r.json()
    return data["outcomes"][0]["price"]

def send_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def main():
    markets = get_markets(SLUG)
    if not markets:
        send_msg("❌ Aucun marché trouvé.")
        return

    for m in markets:
        price = get_price(m["id"])
        print(f"{m['question']} : {price}")

        if price >= THRESHOLD:
            send_msg(
                f"🔥 ALERTE !\n"
                f"📈 Marché : {m['question']}\n"
                f"➡️ Probabilité : {price*100:.1f}%\n"
                f"🔺 Dépasse {THRESHOLD*100:.0f}%"
            )

if __name__ == "__main__":
    main()
