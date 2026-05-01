from flask import Flask, jsonify, request
from datetime import date
import requests

app = Flask(__name__)

LOCATION = 30

@app.route("/menu")
def menu():
    today = date.today().isoformat()
    meal = request.args.get("meal", "1")

    menu_resp = requests.get(
        "https://api.cs50.io/dining/menus",
        params={"location": LOCATION, "date": today, "meal": meal}
    ).json()

    recipe_ids = list({item["recipe"] for item in menu_resp})
    names = []
    for rid in recipe_ids:
        r = requests.get(f"https://api.cs50.io/dining/recipes/{rid}").json()
        names.append(r["name"])

    return jsonify({"meal": int(meal), "date": today, "items": sorted(names)})

if __name__ == "__main__":
    app.run(port=5000)