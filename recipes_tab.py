import pandas as pd
import os
from utils import parse_instructions, parse_ingredients_and_measurements, extract_ingredients

def load_recipes_data(base_dir):
    recipes_parquet_file_path = os.path.join(base_dir, 'recipes.parquet')
    recipes_df = pd.read_parquet(recipes_parquet_file_path)

    # Map columns from recipes_df to match meals_df
    recipes_df = recipes_df.rename(columns={
        'name': 'strMeal',
        'description': 'strInstructions',
        'thumbnail_url': 'strMealThumb',
        'tags': 'strTags',
        'country': 'strArea',
        'keywords': 'strCategory',
        'inspired_by_url': 'strSource',
        'original_video_url': 'original_video_url'  # Correctly map the original_video_url column
    })

    # Convert sections column to string for display
    recipes_df['sections'] = recipes_df['sections'].astype(str)

    # Parse instructions
    recipes_df['parsed_instructions'] = recipes_df['instructions'].apply(parse_instructions)

    # Parse ingredients and measurements
    recipes_df['parsed_ingredients'] = recipes_df['sections'].apply(parse_ingredients_and_measurements)

    # Extract ingredients for search
    recipes_df['search_ingredients'] = recipes_df['sections'].apply(extract_ingredients)

    # Use search_ingredients for isolated_ingredients
    recipes_df['isolated_ingredients'] = recipes_df['search_ingredients']

    return recipes_df