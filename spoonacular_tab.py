import pandas as pd
import os
import json
from bs4 import BeautifulSoup
from utils import extract_ingredients

def parse_ingredients(ingredients_str):
    if not isinstance(ingredients_str, str):
        return ""
    try:
        ingredients_list = ingredients_str.split(', ')
        numbered_list = [f"{i + 1}. {ingredient}" for i, ingredient in enumerate(ingredients_list)]
        return '\n'.join(numbered_list)
    except (ValueError, SyntaxError):
        return ""

def parse_instructions(instructions_str):
    if instructions_str is None:
        return ""
    try:
        soup = BeautifulSoup(instructions_str, 'html.parser')
        steps = soup.find_all('li')
        numbered_steps = [f"{i + 1}. {step.get_text(strip=True)}" for i, step in enumerate(steps)]
        return '\n'.join(numbered_steps)
    except Exception:
        return ""

def load_spoonacular_data(base_dir):
    spoonacular_parquet_file_path = os.path.join(base_dir, 'spoonacular.parquet')
    spoonacular_df = pd.read_parquet(spoonacular_parquet_file_path)

    spoonacular_df = spoonacular_df.rename(columns={
        'title': 'strMeal',
        'instructions': 'strInstructions',
        'image': 'strMealThumb',
        'sourceUrl': 'strSource',
        'author': 'original_video_url'
    })

    spoonacular_df['ingredients'] = spoonacular_df['ingredients'].astype(str)
    spoonacular_df['parsed_ingredients_spoonacular'] = spoonacular_df['ingredients'].apply(parse_ingredients)
    spoonacular_df['search_ingredients'] = spoonacular_df['parsed_ingredients_spoonacular'].apply(extract_ingredients)
    spoonacular_df['temp_parsed_instructions'] = spoonacular_df['strInstructions'].apply(parse_instructions)
    spoonacular_df['parsed_strInstructions'] = spoonacular_df['temp_parsed_instructions']

    def get_isolated_ingredients(ingredients_str):
        if not ingredients_str:
            return ''
        try:
            ingredients_list = ingredients_str.split(', ')
            return ', '.join(ingredients_list)
        except Exception:
            return ''

    spoonacular_df['isolated_ingredients'] = spoonacular_df['ingredients'].apply(get_isolated_ingredients)

    return spoonacular_df