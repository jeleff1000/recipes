import streamlit as st
import pandas as pd
import re
import json
import os
from utils import search_bar, get_combined_categories, parse_ingredients_and_measurements, parse_instructions, extract_ingredients
from meals_tab import load_meals_data
from recipes_tab import load_recipes_data

base_dir = os.path.dirname(__file__)

# Load the data
meals_df = load_meals_data(base_dir)
recipes_df = load_recipes_data(base_dir)

# Add an index to each DataFrame
meals_df['source'] = 'meals'
recipes_df['source'] = 'recipes'

# Combine the two DataFrames
combined_df = pd.concat([meals_df, recipes_df], ignore_index=True)

# Load existing ratings
ratings_file_path = os.path.join(base_dir, 'ratings.json')
if os.path.exists(ratings_file_path):
    with open(ratings_file_path, 'r') as f:
        ratings = json.load(f)
else:
    ratings = {}

# Get combined categories
combined_categories = get_combined_categories(combined_df, combined_df)

# Function to convert star rating string to numeric value
def star_rating_to_numeric(star_rating):
    star_map = {
        '★★★★★': 5,
        '★★★★☆': 4,
        '★★★☆☆': 3,
        '★★☆☆☆': 2,
        '★☆☆☆☆': 1,
        '☆☆☆☆☆': 0
    }
    return star_map.get(star_rating, 0)

# Function to combine ingredients and measurements for meals
def combine_ingredients_and_measurements(row):
    ingredients = []
    count = 1
    for i in range(1, 21):
        ingredient = row.get(f'strIngredient{i}')
        measurement = row.get(f'strMeasure{i}')
        if pd.notna(ingredient) and pd.notna(measurement) and ingredient.strip() and measurement.strip():
            ingredients.append(f"{count}. {measurement} {ingredient}")
            count += 1
        elif pd.notna(ingredient) and ingredient.strip():
            ingredients.append(f"{count}. {ingredient}")
            count += 1
    return '\n'.join(ingredients)

# Function to convert instructions to numbered list
def convert_instructions_to_numbered_list(instructions):
    if instructions is None:
        return ""
    steps = instructions.split('\n')
    numbered_steps = [f"{i+1}. {step.strip()}" for i, step in enumerate(steps) if step.strip()]
    return '\n'.join(numbered_steps)

# Apply the functions to the combined DataFrame
combined_df['ingredients'] = combined_df.apply(lambda row: combine_ingredients_and_measurements(row) if row['source'] == 'meals' else parse_ingredients_and_measurements(row['sections']), axis=1)
combined_df['strInstructions'] = combined_df.apply(lambda row: convert_instructions_to_numbered_list(row['strInstructions']) if row['source'] == 'meals' else parse_instructions(row['instructions']), axis=1)

# Streamlit app with a single tab
st.title("Combined Meals and Recipes Data")

# Use the centralized search bar
search_results = search_bar(combined_df, combined_categories, prefix='combined_')
meal_search, category_search, area_search, tags_search, ingredients_search, min_star_rating, vegetarian_filter, kosher_filter, margarine_for_butter, applesauce_for_oil, greek_yogurt_for_sour_cream, honey_for_sugar, num_ingredients = search_results

# Map the num_ingredients to their corresponding ranges
ingredient_ranges = {
    'Less (0-5)': (0, 5),
    'Moderate (6-10)': (6, 10),
    'More (11+)': (11, float('inf'))
}
min_ingredients, max_ingredients = ingredient_ranges.get(num_ingredients, (None, None))

# Apply substitutions
combined_df['ingredients'] = combined_df['ingredients'].fillna('')
if margarine_for_butter:
    combined_df['ingredients'] = combined_df['ingredients'].apply(lambda x: re.sub(r'(?i)butter', 'margarine', x))
if applesauce_for_oil:
    combined_df['ingredients'] = combined_df['ingredients'].apply(lambda x: re.sub(r'(?i)oil', 'applesauce', x))
if greek_yogurt_for_sour_cream:
    combined_df['ingredients'] = combined_df['ingredients'].apply(lambda x: re.sub(r'(?i)sour cream', 'greek yogurt', x))
if honey_for_sugar:
    combined_df['ingredients'] = combined_df['ingredients'].apply(lambda x: re.sub(r'(?i)sugar', 'honey', x))

# Filter the DataFrame based on the search terms
if meal_search or category_search or area_search or tags_search or ingredients_search or min_star_rating or vegetarian_filter or kosher_filter or num_ingredients:
    if meal_search:
        combined_df = combined_df[combined_df['strMeal'].str.contains(meal_search, case=False, na=False)]
    if category_search:
        combined_df = combined_df[combined_df['strTags'].str.contains(category_search, case=False, na=False)]
    if area_search:
        combined_df = combined_df[combined_df['strTags'].str.contains(area_search, case=False, na=False)]
    if tags_search:
        tags = tags_search.split()
        for tag in tags:
            combined_df = combined_df[combined_df['strTags'].str.contains(tag, case=False, na=False)]
    if ingredients_search:
        ingredients = re.findall(r'"(.*?)"|(\S+)', ingredients_search)
        ingredients = [item[0] or item[1] for item in ingredients]
        for ingredient in ingredients:
            if ' ' in ingredient:
                combined_df = combined_df[combined_df['ingredients'].str.contains(re.escape(ingredient), case=False, na=False)]
            else:
                combined_df = combined_df[combined_df['ingredients'].str.contains(ingredient, case=False, na=False)]
    if min_star_rating:
        if min_star_rating != '':
            min_star_rating_numeric = star_rating_to_numeric(min_star_rating)
            combined_df['avg_rating'] = combined_df.apply(lambda row: ratings.get(row['strMeal'], {'total': 0, 'count': 0})['total'] / ratings.get(row['strMeal'], {'total': 0, 'count': 0})['count'] if ratings.get(row['strMeal'], {'total': 0, 'count': 0})['count'] > 0 else 0, axis=1)
            combined_df = combined_df[combined_df['avg_rating'] >= min_star_rating_numeric]
    if vegetarian_filter:
        combined_df = combined_df[combined_df['strTags'].str.contains('Vegetarian', case=False, na=False)]
    if kosher_filter:
        combined_df = combined_df[~combined_df['ingredients'].str.contains('shrimp|pork', case=False, na=False)]
        combined_df = combined_df[~((combined_df['ingredients'].str.contains('meat|beef|lamb|chicken', case=False, na=False)) & (combined_df['ingredients'].str.contains('milk|cheese|yogurt|butter|sour cream', case=False, na=False)))]
    if min_ingredients is not None and max_ingredients is not None:
        combined_df = combined_df[combined_df['ingredients'].apply(lambda x: min_ingredients <= len(x.split('\n')) <= max_ingredients)]

    # Sort the DataFrame alphabetically by 'strMeal'
    if 'strMeal' in combined_df.columns:
        combined_df = combined_df.sort_values(by='strMeal', ascending=True)
    else:
        st.error("Column 'strMeal' not found in the DataFrame")

    # Display the DataFrame
    for index, row in combined_df.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("<br><br>", unsafe_allow_html=True)  # Add vertical space above the image
            st.image(row['strMealThumb'], caption=row['strMeal'], use_container_width=True)
        with col2:
            st.subheader(row['strMeal'])

            # Rating section
            meal_id = row['strMeal']
            current_rating = ratings.get(meal_id, {'total': 0, 'count': 0})
            avg_rating = current_rating['total'] / current_rating['count'] if current_rating['count'] > 0 else 0
            st.write(f"**Average Rating:** {avg_rating:.2f} ({current_rating['count']} ratings)")

            rating = st.feedback(options="stars", key=f'rating_{index}')
            if rating is not None and st.button('Submit Rating', key=f'submit_{index}'):
                if meal_id not in ratings:
                    ratings[meal_id] = {'total': 0, 'count': 0}
                ratings[meal_id]['total'] += rating + 1  # Adjust rating to be 1-based
                ratings[meal_id]['count'] += 1
                with open(ratings_file_path, 'w') as f:
                    json.dump(ratings, f)
                st.success('Rating submitted!')

            with st.expander("Ingredients and Measurements"):
                st.write(row['ingredients'])  # Display combined ingredients and measurements

            with st.expander("Instructions"):
                st.write(row['strInstructions'])  # Display instructions

            # Display video based on source
            if row['source'] == 'meals' and 'strYoutube' in row and isinstance(row['strYoutube'], str) and row['strYoutube']:
                with st.expander("Video"):
                    st.video(row['strYoutube'])
            elif row['source'] == 'recipes' and 'original_video_url' in row and isinstance(row['original_video_url'], str) and row['original_video_url']:
                with st.expander("Video"):
                    st.video(row['original_video_url'])

            st.write(f"**Source:** {row['strSource']}")
else:
    st.write("Please enter search criteria to display results.")