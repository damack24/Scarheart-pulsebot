from flask import Flask, render_template, request, redirect, session, send_from_directory, send_file
import json, os, zipfile
from datetime import datetime, date
from random import choice

app = Flask(__name__)
app.secret_key = "scarheart_secret"

# Load + save helpers
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# Load data files
users = load_json("users.json", {})
store = load_json("store.json", [])

# Quotes
quotes = [
    "Scars remind us where we've been, but don’t have to dictate where we’re going.",
    "Even a broken heart keeps beating.",
    "There is beauty in the burn and strength in survival.",
    "Pulse through the pain — become your own legend.",
    "Every heartbeat etches a new chapter in your resurrection."
]

# Scar Challenges
scar_challenges = [
    "Write one sentence about what hurt you but taught you.",
    "Draw your pain using only 3 lines.",
    "Speak a truth you’ve been hiding from yourself.",
    "Take a deep breath, name what you’re grateful for right now.",
    "What is one scar you wear with pride?",
    "Who would you be if fear had no voice?",
    "What does your heartbeat sound like today?",
    "What would ScarHeart tell the younger you?",
]

def get_daily_challenge():
    today = date.today().toordinal()
    return scar_challenges[today % len(scar_challenges)]

# Routes
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users.get(email)
        if user and user["password"] == password:
            session["user"] = email
            return redirect("/pulse")
        return "Invalid login"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email in users:
            return "Email already registered"
        users[email] = {"password": password, "tokens": 0, "history": []}
        save_json("users.json", users)
        return redirect("/login")
    return render_template("register.html")

@app.route("/pulse", methods=["GET", "POST"])
def pulse():
    if "user" not in session:
        return redirect("/login")
    email = session["user"]
    user = users[email]

    message = None
    if request.method == "POST":
        mood = request.form["mood"]
        reflection = request.form.get("reflection", "").strip()
        challenge = get_daily_challenge()
        user["tokens"] += 1
        user["history"].append({
            "date": str(datetime.now().date()),
            "mood": mood,
            "challenge": challenge,
            "reflection": reflection
        })
        save_json("users.json", users)
        message = f"ScarHeart hears you... +1 Token for staying present through the {mood}."

    return render_template(
        "pulse.html",
        quote=choice(quotes),
        tokens=user["tokens"],
        message=message,
        challenge=get_daily_challenge()
    )

@app.route("/store", methods=["GET", "POST"])
def store_route():
    if "user" not in session:
        return redirect("/login")
    email = session["user"]
    user = users[email]

    message = None
    if request.method == "POST":
        selected = request.form["item"]
        if selected == "all":
            if user["tokens"] >= 10:
                user["tokens"] -= 10
                save_json("users.json", users)
                zip_path = "rewards_bundle.zip"
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for item in store:
                        file_path = os.path.join("rewards", item["file"])
                        if os.path.exists(file_path):
                            zipf.write(file_path, arcname=item["file"])
                return send_file(zip_path, as_attachment=True)
            else:
                message = "Not enough tokens for full unlock."
        else:
            index = int(selected)
            item = store[index]
            if user["tokens"] >= item["price"]:
                user["tokens"] -= item["price"]
                save_json("users.json", users)
                return send_from_directory("rewards", item["file"], as_attachment=True)
            else:
                message = "Not enough tokens."

    return render_template("store.html", store=store, tokens=user["tokens"], message=message)

@app.route("/journal")
def journal():
    if "user" not in session:
        return redirect("/login")
    email = session["user"]
    user = users[email]
    history = user.get("history", [])
    return render_template("journal.html", history=history)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
