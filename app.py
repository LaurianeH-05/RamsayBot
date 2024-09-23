from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import string

app = Flask(__name__)
CORS(app) 

API_KEY = "5c6bdea8078e4ced966da4be372fe44c"

def clean_message(message):
    return re.sub(r"[\*\_]+", "", message)

def get_recipe_from_api(query):
    url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}"
    response = requests.get(url, params={"query": query})

    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            recipe_id = data['results'][0].get('id')  # Get the recipe ID
            title = data['results'][0].get('title', 'Unknown Title')

            # Fetch detailed recipe information using the ID
            recipe_details = get_recipe_details(recipe_id)
            return f"Here's a recipe for {title}:\n{recipe_details}"
    return "Sorry, I couldn't find a recipe for that."

def get_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        ingredients = [ingredient['name'] for ingredient in data['extendedIngredients']]
        instructions = data['instructions']
        return f"**Ingredients:**\n" + "\n".join(ingredients) + f"\n\n**Instructions:**\n{instructions}"
    return "Sorry, I couldn't fetch the recipe details."

def suggest_meals(allergies=None, dietary_restriction=None, cuisine=None):
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": API_KEY,
        "diet": dietary_restriction,
        "cuisine": cuisine,
        "excludeIngredients": ','.join(allergies) if allergies else None,
        "number": 4
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        meals = []
        for result in data.get("results", []):
            meals.append({
                "name": result.get('title', 'Unknown Title'),
                "url": result.get('sourceUrl', 'No URL found')
            })
        return meals if meals else [{"name": "No meals found based on your preferences."}]
    else:
        return [{"name": "Error fetching meal suggestions."}]

def extract_allergies(message):
    if "allergy" in message:
        # Assume the format "I have allergies to: peanuts, dairy"
        start = message.lower().find("allergy")
        allergies_part = message[start:].split(":")[-1].strip()
        return [allergen.strip() for allergen in allergies_part.split(",")]
    return []

def extract_dietary_restriction(message):
    if "diet" in message:
        # Assume the format "I am on a dairy-free diet"
        start = message.lower().find("diet")
        diet_part = message[start:].split(":")[-1].strip()
        return diet_part
    return None

def extract_cuisine(message):
    if "cuisine" in message:
        # Assume the format "I prefer Italian cuisine"
        start = message.lower().find("cuisine")
        cuisine_part = message[start:].split(":")[-1].strip()
        return cuisine_part
    return None


def get_cooking_tip(topic):
    tips = {
        "clean bell pepper": "To clean a bell pepper, rinse it under cold water, cut off the top, remove seeds, and slice as desired.",
        "reduce food waste": "To reduce food waste, consider making stocks from vegetable scraps or composting.",
        "cut onion": "",
        "clean red meat": "",
        "clean poultry": "",
    }
    return tips.get(topic.lower(), "Sorry, I don't have a tip for that.")

def convert_metric_to_cups(metric, amount):
    conversions = {
        "tablespoon": amount * 1 / 16,
        "teaspoon": amount * 1 / 48,
        "cup": amount * 1 / 1,
    }
    return conversions.get(metric.lower(), "Sorry, I don't have that conversion.")

def get_substitution(ingredient):
    substitutions = {
        "flour": ["almond flour", "coconut flour", "whole wheat flour"],
        "sugar": ["honey"],
        "eggs": ["flax (1tbsp + 3tbsp water)", "applesauce (1/4 cup)", "silken tofu(1/4 cup)"],
        "cornstarch" : ["baking soda"],
        "milk": ["oat milk", "almond milk", "soy milk"],
        "butter": ["coconut oil", "applesauce", "greek yogurt"],
        "sugar" : ["honey", "maple syrup"],
        "pasta" : ["Zoodles", "spaghetti squash", "quinoa"],
        "rice" : ["cauliflower rice", "quinoa", "farro"],
        "cheese" : ["nutritional yeast", "cashew cheese", "tofu"],
        "ground beef" : ["lentils", "ground turkey", "black beans"],
        "bread" : ["lettuce wraps", "sweet potato slices"],
        }
    return substitutions.get(ingredient.lower(), "Sorry I dont have a substitution for that.")
    
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")

        response = handle_user_message(user_message)

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_user_message(message):
    message = message.rstrip(string.punctuation)

    if "substitution for" in message:
        ingredient = message.split("substitution for")[-1].strip()
        return get_substitution(ingredient)
    elif "recipe" in message:
        query = message.split("recipe")[-1].strip()
        response = get_recipe_from_api(query)
        if response:
            return response
        return "I didn't understand that. Can you rephrase?"
    elif any(idea in message for idea in ["dinner idea", "lunch idea", "breakfast idea"]):
        return (
            "Sure! Please provide the following information:\n"
            "- **Allergies** (e.g., peanuts, dairy):\n"
            "- **Dietary Restrictions** (e.g., vegetarian, gluten-free):\n"
            "- **Cuisine** (e.g., Italian, Mexican):\n"
            "You can format your message like this:\n"
            "'I have allergies to: peanuts, dairy. I'm on a vegetarian diet and prefer Italian cuisine.'"
        )
    allergies = extract_allergies(message)
    dietary_restriction = extract_dietary_restriction(message)
    cuisine = extract_cuisine(message)

    if allergies or dietary_restriction or cuisine:
        meals = suggest_meals(allergies, dietary_restriction, cuisine)
        response = "Here are some meal suggestions:\n"
        response += "\n".join(f"{meal['name']}: {meal['url']}" for meal in meals)
        return response
    
    elif "convert" in message:
        try:
            metric, amount = message.split("convert")[-1].strip().split("to")
            return convert_metric_to_cups(metric.strip(), float(amount.strip()))
        except ValueError:
            return "I didn't understand that. Can you rephrase?"
    return "Sorry, I didn't understand your question. Please try again."

if __name__ == "__main__":
    app.run(debug=True)