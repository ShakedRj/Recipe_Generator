import requests
from environs import Env
import os

# Load environment variables from .env file
env= Env()
env.read_env()
# Retrieve the API key from the environment variable
api_key = env.str("SPOON_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the SPOON_API_KEY environment variable.")

def recipe_search(search_string):
    base_url = 'https://api.spoonacular.com'
    search_endpoint = f'{base_url}/recipes/complexSearch'
    params = {
        'query': search_string,
        'apiKey': api_key
    }
    response = requests.get(search_endpoint, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Process the JSON data
        recipes = data.get('results', [])
        return_rec=[]
        for recipe in recipes:
            rec=[]
            recipe_id = recipe['id'] 
            details_endpoint = f'{base_url}/recipes/{recipe_id}/information'
            params = {
                'apiKey': api_key
            }
            response = requests.get(details_endpoint, params=params)
            if response.status_code == 200:
                recipe_details = response.json()
                rec.append(recipe_details['title'])
                rec.append(f"Ingredients:")
                for ingredient in recipe_details['extendedIngredients']:
                    rec.append(f" - {ingredient['original']}")
                rec.append(f"Instructions: {recipe_details['instructions']}\n\n")
            else:
                return (f"Error: {response.status_code}")
            return_rec.append(rec)
        return return_rec
    else:
        return (f"Error: {response.status_code}")

