import pandas as pd
import os
import json
import ast
from bs4 import BeautifulSoup
from utils import extract_ingredients
import io
import sys

def parse_ingredients(ingredients_str):
    if not isinstance(ingredients_str, str):
        return ""
    try:
        # Split the ingredients string into a list
        ingredients_list = ingredients_str.split(', ')

        # Create a numbered list
        numbered_list = [f"{i + 1}. {ingredient}" for i, ingredient in enumerate(ingredients_list)]
        return '\n'.join(numbered_list)
    except (ValueError, SyntaxError) as e:
        return ""

def parse_instructions(instructions_str):
    if instructions_str is None:
        return ""
    try:
        # Parse the HTML instructions
        soup = BeautifulSoup(instructions_str, 'html.parser')
        steps = soup.find_all('li')
        numbered_steps = [f"{i + 1}. {step.get_text(strip=True)}" for i, step in enumerate(steps)]
        return '\n'.join(numbered_steps)
    except Exception as e:
        return ""

def parse_extended_ingredients(extended_ingredients_str):
    """Parse the extendedIngredients column to extract ingredients and measurements."""
    try:
        # Fix the syntax issues in the data (convert `array` to a list and add commas between dictionaries)
        extended_ingredients_str = extended_ingredients_str.replace("array(", "[").replace(", dtype=object)", "]")
        extended_ingredients_str = extended_ingredients_str.replace("} {", "}, {")

        # Parse the fixed data into Python objects
        extended_ingredients = json.loads(extended_ingredients_str.replace("'", '"'))

        ingredients_list = []
        for i, ingredient in enumerate(extended_ingredients, start=1):
            original = ingredient.get('original', '')
            if original:
                ingredients_list.append(f"{i}. {original}")
        return '\n'.join(ingredients_list)
    except (ValueError, SyntaxError, json.JSONDecodeError):
        return ''

def load_spoonacular_data(base_dir):
    spoonacular_parquet_file_path = os.path.join(base_dir, 'spoonacular.parquet')
    spoonacular_df = pd.read_parquet(spoonacular_parquet_file_path)

    # Map columns from spoonacular_df to match meals_df
    spoonacular_df = spoonacular_df.rename(columns={
        'title': 'strMeal',
        'instructions': 'strInstructions',
        'image': 'strMealThumb',
        'sourceUrl': 'strSource',
        'author': 'original_video_url'
    })

    # Convert ingredients column to string for display
    spoonacular_df['ingredients'] = spoonacular_df['ingredients'].astype(str)

    # Parse ingredients and create a numbered list
    spoonacular_df['parsed_ingredients_spoonacular'] = spoonacular_df['ingredients'].apply(parse_ingredients)

    # Extract ingredients for search
    spoonacular_df['search_ingredients'] = spoonacular_df['parsed_ingredients_spoonacular'].apply(extract_ingredients)

    # Parse instructions and store in a temporary column
    spoonacular_df['temp_parsed_instructions'] = spoonacular_df['strInstructions'].apply(parse_instructions)

    # Create a new column for parsed instructions
    spoonacular_df['parsed_strInstructions'] = spoonacular_df['temp_parsed_instructions']

    # Capture print output and store in a new column
    def capture_print_output(extended_ingredients_str):
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        print(parse_extended_ingredients(extended_ingredients_str))
        output = new_stdout.getvalue().strip()
        sys.stdout = old_stdout
        return output

    spoonacular_df['print_output'] = spoonacular_df['extendedIngredients'].apply(capture_print_output)

    return spoonacular_df