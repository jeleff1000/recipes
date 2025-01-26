import streamlit as st
from utils import search_bar, parse_singular_ingredients, parse_instructions
import re
import pandas as pd

def display_recipes_tab(recipes_df, combined_categories):
    st.title('Recipes Data')

    # Parse singular and plural ingredient names
    recipes_df[['parsed_ingredients', 'search_ingredients']] = recipes_df['sections'].apply(parse_singular_ingredients).apply(pd.Series)
    # Parse instructions
    recipes_df['parsed_instructions'] = recipes_df['instructions'].apply(parse_instructions)

    # Use the centralized search bar with a unique prefix
    search_results = search_bar(recipes_df, combined_categories, prefix='recipes_')
    meal_search, category_search, area_search, tags_search, ingredients_search, vegetarian_filter, kosher_filter, margarine_for_butter, applesauce_for_oil, greek_yogurt_for_sour_cream, honey_for_sugar = search_results

    # Apply substitutions
    recipes_df['ingredients'] = recipes_df['ingredients'].fillna('')
    if margarine_for_butter:
        recipes_df['ingredients'] = recipes_df['ingredients'].apply(lambda x: re.sub(r'(?i)butter', 'margarine', x))
    if applesauce_for_oil:
        recipes_df['ingredients'] = recipes_df['ingredients'].apply(lambda x: re.sub(r'(?i)oil', 'applesauce', x))
    if greek_yogurt_for_sour_cream:
        recipes_df['ingredients'] = recipes_df['ingredients'].apply(lambda x: re.sub(r'(?i)sour cream', 'greek yogurt', x))
    if honey_for_sugar:
        recipes_df['ingredients'] = recipes_df['ingredients'].apply(lambda x: re.sub(r'(?i)sugar', 'honey', x))

    # Filter the DataFrame based on the search terms
    if meal_search or category_search or area_search or tags_search or ingredients_search or vegetarian_filter or kosher_filter:
        if meal_search:
            recipes_df = recipes_df[recipes_df['strMeal'].str.contains(meal_search, case=False, na=False)]
        if category_search:
            recipes_df = recipes_df[recipes_df['strTags'].str.contains(category_search, case=False, na=False)]
        if area_search:
            recipes_df = recipes_df[recipes_df['strTags'].str.contains(area_search, case=False, na=False)]
        if tags_search:
            tags = tags_search.split()
            for tag in tags:
                recipes_df = recipes_df[recipes_df['strTags'].str.contains(tag, case=False, na=False)]
        if ingredients_search:
            ingredients = re.findall(r'"(.*?)"|(\S+)', ingredients_search)
            ingredients = [item[0] or item[1] for item in ingredients]
            for ingredient in ingredients:
                if ' ' in ingredient:
                    recipes_df = recipes_df[recipes_df['search_ingredients'].str.contains(re.escape(ingredient), case=False, na=False)]
                else:
                    recipes_df = recipes_df[recipes_df['search_ingredients'].str.contains(ingredient, case=False, na=False)]
        if vegetarian_filter:
            recipes_df = recipes_df[recipes_df['strTags'].str.contains('Vegetarian', case=False, na=False)]
        if kosher_filter:
            recipes_df = recipes_df[~recipes_df['search_ingredients'].str.contains('shrimp|pork', case=False, na=False)]
            recipes_df = recipes_df[~((recipes_df['search_ingredients'].str.contains('meat|beef|lamb|chicken', case=False, na=False)) & (recipes_df['search_ingredients'].str.contains('milk|cheese|yogurt|butter|sour cream', case=False, na=False)))]

        # Sort the DataFrame alphabetically by 'strMeal'
        if 'strMeal' in recipes_df.columns:
            recipes_df = recipes_df.sort_values(by='strMeal', ascending=True)
        else:
            st.error("Column 'strMeal' not found in the DataFrame")

        # Display the DataFrame
        for index, row in recipes_df.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("<br><br>", unsafe_allow_html=True)  # Add vertical space above the image
                st.image(row['strMealThumb'], caption=row['strMeal'], use_container_width=True)
            with col2:
                st.subheader(row['strMeal'])
                with st.expander("Instructions"):
                    st.write(row['parsed_instructions'])
                st.write(f"**Source:** {row['strSource']}")
                with st.expander("Video"):
                    st.video(row['youtube'])
                st.write(f"**Ingredients:** {row['parsed_ingredients']}")