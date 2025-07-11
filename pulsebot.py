import json, random, datetime, os

# === Quotes ===
pulse_quotes = [
    "Your scars are ink. Write your story.",
    "Pain doesn’t mean pause—it means power.",
    "Even silence has a rhythm. Listen.",
    "You survived. That’s the first verse of your legacy."
]

mood_responses = {
    "good": "Ride that wave. Let it carry your next creation.",
    "okay": "Hold the beat steady. Even the middle matters.",
    "bad": "Dark doesn’t mean dead. There’s movement in shadows.",
    "angry": "Let the fire forge, not destroy. Channel it.",
    "sad": "Tears are soul notes leaking out. Play them raw."
}

# === Files ===
LOG_FILE = "pulse_log.json"
TOKENS_FILE = "tokens.json"
STORE_FILE = "store.json"
REWARDS_DIR = "rewards"

# === Load/Init Files ===
def load_json(path, default):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default

pulse_log = load_json(LOG_FILE, [])
tokens = load_json(TOKENS_FILE, {"scar_tokens": 0})
store = load_json(STORE_FILE, [])

# === Save Helpers ===
def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# === Store System ===
def open_store():
    print("\n🛍️ ScarHeart Token Store")
    print("━━━━━━━━━━━━━━━━━━━━━━━")
    for i, item in enumerate(store):
        print(f"{i+1}. {item['name']} – {item['price']} tokens")

    choice = input("\nPick item number to buy or [enter] to skip: ").strip()
    if not choice: return
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(store):
        print("❌ Invalid choice.")
        return

    index = int(choice) - 1
    item = store[index]
    if tokens['scar_tokens'] < item['price']:
        print("🚫 Not enough ScarTokens.")
        return

    # Deduct + "deliver"
    tokens['scar_tokens'] -= item['price']
    save_json(TOKENS_FILE, tokens)

    print(f"✅ Unlocked: {item['name']}")
    print(f"📁 Check: {REWARDS_DIR}/{item['file']}")
    print(f"💎 ScarTokens left: {tokens['scar_tokens']}")

# === PulseBot ===
def run_pulse_bot():
    today = str(datetime.date.today())
    print("\n💔 SCARHEART PULSE •", today)
    print("━━━━━━━━━━━━━━━━━━━━━━")

    quote = random.choice(pulse_quotes)
    print(f"🩸 Pulse: “{quote}”")
    
    mood = input("\nWhere’s your mind today? (good / okay / bad / angry / sad): ").lower().strip()
    if mood not in mood_responses:
        print("⚠️ Choose: good / okay / bad / angry / sad.")
        return

    print(f"\nScar responds: {mood_responses[mood]}")

    pulse_log.append({"date": today, "mood": mood})
    tokens['scar_tokens'] += 1

    save_json(LOG_FILE, pulse_log)
    save_json(TOKENS_FILE, tokens)

    print(f"\n💎 +1 ScarToken earned. Total: {tokens['scar_tokens']}")
    
    open_store()

# === Run ===
if __name__ == "__main__":
    run_pulse_bot()
