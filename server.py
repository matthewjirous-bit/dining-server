from flask import Flask, jsonify, request
from datetime import date
import requests

app = Flask(__name__)
LOCATION = 30

IGNORE = {
    "butter", "margarine", "ketchup", "mustard", "mayonnaise packets",
    "tartar sauce", "soy sauce", "hot sauce", "ranch dressing",
    "balsamic dressing (pc)", "italian lite dressing (pc)",
    "italina lite dressing (pc)", "suntan lime vinaigrette",
    "sesame lime vinaigrette", "buttermilk dressing (pc)",
    "no nut basil pesto", "ranch buttermilk dressing (pc)",
    "grape preserves", "teddy's peanut butter & grape jelly on wheat",
    "1% milk 8z", "skim milk 8 oz.", "chocolate milk 8 oz.",
    "can of coke", "can of diet coke", "tropicana orange juice 10z",
    "cranberry lime seltzer", "pomegranate seltzer water",
    "water alum can 12oz", "plain soy milk",
    "hard cooked eggs", "cage free hard boiled eggs",
    "salt", "pepper", "sugar", "creamer",
    "lemon wedges", "sliced tomatoes", "sliced red onions",
    "sliced avocado", "sliced cucumbers", "shredded carrots",
    "peeled baby carrots", "baby arugula", "little leaf greens",
    "leaf lettuce", "corn niblets", "cranberries", "grape tomatoes",
    "sliced white american cheese", "mozzarella, tomato & basil wrap",
    "wheat tortillas", "gluten free white bread", "hearty white bread",
    "homemade white bread", "ham & swiss on hearty wheat",
    "turkey & cheddar on wheat", "turkey & ckeddar on gluten free wrap",
    "turkey & cheddar on gluten free wrap",
    "tuna salad and lettuce on spinach wrap",
    "chicken and lettuce wrap", "bread, hearty wheat",
    "gluten free multi grain bread", "assorted bagels",
    "oatmeal raisin cookies", "daily baked cookie",
    "pastry of the day", "orange soft serve", "raspberry soft serve",
    "quaker instant oatmeal cups", "granola",
    "all natural peanut butter", "fruit, bananas", "fruit, local apples",
    "fruit, oranges", "diced onions", "mustard packets",
    "huds boom sauce", "kalamata olives", "kalamala olives",
    "chips, cape cod", "pretzel twists", "suntan pepper strips",
    "kosher dill pickle chips", "portobello saltado",
    "flaked tuna", "fly by harvest salad",
    "cream cheese packets asst.", "hard cooked eggs",
}

CATEGORIES = {
    "Soup": ["soup", "chowder", "bisque", "stew"],
    "Mains": ["chicken", "fish", "beef", "steak", "salmon", "shrimp",
              "turkey", "pork", "lamb", "tofu", "falafel", "halal",
              "breast", "roasted", "grilled", "battered", "fried"],
    "Sides": ["rice", "quinoa", "barley", "corn", "potato", "fries",
              "yucca", "broccoli", "squash", "cauliflower",
              "steamed", "roasted vegetable", "tabouleh", "guacamole"],
    "Salads": ["salad", "slaw", "greens"],
    "Cheese & Deli": ["cheese", "ham", "sliced ham"],
    "Yogurt & Dairy": ["yogurt", "dairy free"],
}

def categorize(name):
    lower = name.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in lower:
                return category
    return "Other"

@app.route("/menu")
def menu():
    today = date.today().isoformat()
    meal_str = request.args.get("meal", "1")
    try:
        meal_int = int(meal_str)
    except ValueError:
        meal_int = 1

    if meal_int not in [0, 1, 2]:
        meal_int = 1

    menu_resp = requests.get(
        "https://api.cs50.io/dining/menus",
        params={"location": LOCATION, "date": today, "meal": meal_int}
    ).json()

recipe_ids = list({item["recipe"] for item in menu_resp})
names = []
session = requests.Session()
for rid in recipe_ids:
    try:
        r = session.get(
            f"https://api.cs50.io/dining/recipes/{rid}",
            timeout=5
        ).json()
        name = r["name"]
        if name.lower() not in IGNORE:
            names.append(name)
    except Exception:
        pass
session.close()

    categorized = {}
    for name in sorted(names):
        cat = categorize(name)
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(name)

    order = ["Soup", "Mains", "Sides", "Salads", "Cheese & Deli", "Yogurt & Dairy", "Other"]
    result = []
    for cat in order:
        if cat in categorized:
            result.append({"category": cat, "items": categorized[cat]})

    meal_names = {0: "Breakfast", 1: "Lunch", 2: "Dinner"}
    return jsonify({
        "meal": meal_names.get(meal_int, "Lunch"),
        "date": today,
        "categories": result
    })

if __name__ == "__main__":
    app.run(port=5000)
