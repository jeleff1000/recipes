import streamlit as st
import pandas as pd
import re
import json
import os
from utils import search_bar, get_combined_categories

# Paths to the Parquet files
meals_parquet_file_path = 'C:\\Users\\joeye\\OneDrive\\Desktop\\recipes\\meals.parquet'
recipes_parquet_file_path = 'C:\\Users\\joeye\\OneDrive\\Desktop\\recipes\\recipes.parquet'
ratings_file_path = 'C:\\Users\\joeye\\OneDrive\\Desktop\\recipes\\ratings.json'

# Load the Parquet files
meals_df = pd.read_parquet(meals_parquet_file_path)
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
    'original_video_url': 'youtube'
})

# Combine the two DataFrames
combined_df = pd.concat([meals_df, recipes_df], ignore_index=True)

# Load existing ratings
if os.path.exists(ratings_file_path):
    with open(ratings_file_path, 'r') as f:
        ratings = json.load(f)
else:
    ratings = {}

# Get combined categories
combined_categories = get_combined_categories(combined_df, combined_df)

# Streamlit app with a single tab
st.title("Combined Meals and Recipes Data")

# Use the centralized search bar
search_results = search_bar(combined_df, combined_categories, prefix='combined_')
meal_search, category_search, area_search, tags_search, ingredients_search, vegetarian_filter, kosher_filter, margarine_for_butter, applesauce_for_oil, greek_yogurt_for_sour_cream, honey_for_sugar = search_results

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
if any([meal_search, category_search, area_search, tags_search, ingredients_search, vegetarian_filter, kosher_filter]):
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
    if vegetarian_filter:
        combined_df = combined_df[combined_df['strTags'].str.contains('Vegetarian', case=False, na=False)]
    if kosher_filter:
        combined_df = combined_df[~combined_df['ingredients'].str.contains('shrimp|pork', case=False, na=False)]
        combined_df = combined_df[~((combined_df['ingredients'].str.contains('meat|beef|lamb|chicken', case=False, na=False)) & (combined_df['ingredients'].str.contains('milk|cheese|yogurt|butter|sour cream', case=False, na=False)))]

    # Sort the DataFrame alphabetically by 'strMeal'
    combined_df = combined_df.sort_values(by='strMeal', ascending=True)

    # Display the DataFrame
    for index, row in combined_df.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("<br><br>", unsafe_allow_html=True)  # Add vertical space above the image
            st.image(row['strMealThumb'], caption=row['strMeal'], use_container_width=True)
        with col2:
            st.subheader(row['strMeal'])
            with st.expander("Instructions"):
                st.write(row['strInstructions'])
            st.write(f"**Source:** {row['strSource']}")
            if 'youtube' in row and isinstance(row['youtube'], str) and row['youtube']:
                with st.expander("Video"):
                    st.video(row['youtube'])
            st.write(f"**Ingredients:** {row['ingredients']}")

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