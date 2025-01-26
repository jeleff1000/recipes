import streamlit as st
import pandas as pd
import re

def get_combined_categories(recipes_df, meals_df):
    # Define the refined categories
    refined_categories = [
        'Soup', 'Dressing', 'Easy', 'Healthy', 'Salad', 'Dairy Free', 'Snacks', 'Treats',
        'Vegan', 'Vegetarian', 'Dessert', 'Breakfast', 'Baking', 'Side Dish', 'Brunch',
        'Alcohol', 'Dinner'
    ]
    return sorted(refined_categories)

def search_bar(df, categories, prefix=''):
    # Create two columns for the first row of selectboxes
    col1, col2, col3 = st.columns(3)
    with col1:
        meal_search = st.selectbox('Search by Meal:', options=[''] + sorted(df['strMeal'].unique()), index=0, key=f'{prefix}meal_search')
    with col2:
        category_search = st.selectbox('Search by Category:', options=[''] + sorted(categories), index=0, key=f'{prefix}category_search')
    with col3:
        area_search = st.selectbox('Search by Region:', options=[''] + sorted([
            'American', 'British', 'Canadian', 'Chinese', 'Croatian', 'Dutch', 'Egyptian', 'Filipino', 'French', 'Greek',
            'Indian', 'Irish', 'Italian', 'Jamaican', 'Japanese', 'Kenyan', 'Malaysian', 'Mexican', 'Moroccan', 'Polish',
            'Portuguese', 'Russian', 'Spanish', 'Thai', 'Tunisian', 'Turkish', 'Ukrainian', 'Unknown', 'Vietnamese'
        ]), index=0, key=f'{prefix}area_search')

    # Create two columns for the second row of text inputs
    col4, col5, col6 = st.columns(3)
    with col4:
        tags_search = st.text_input('Search by Tags:', key=f'{prefix}tags_search')
    with col5:
        ingredients_search = st.text_input('Search by Ingredients:', key=f'{prefix}ingredients_search')

    # Create columns for checkboxes with thinner width
    col7, col8 = st.columns([1, 1])
    with col7:
        vegetarian_filter = st.checkbox('Vegetarian', key=f'{prefix}vegetarian_filter')
    with col8:
        kosher_filter = st.checkbox('Kosher', key=f'{prefix}kosher_filter')

    # Add a section for common substitutions
    with st.expander("Common Substitutions"):
        margarine_for_butter = st.toggle('Margarine for Butter', key=f'{prefix}margarine_for_butter')
        applesauce_for_oil = st.toggle('Applesauce for Oil', key=f'{prefix}applesauce_for_oil')
        greek_yogurt_for_sour_cream = st.toggle('Greek Yogurt for Sour Cream', key=f'{prefix}greek_yogurt_for_sour_cream')
        honey_for_sugar = st.toggle('Honey for Sugar', key=f'{prefix}honey_for_sugar')

    # Return all search and filter values
    return meal_search, category_search, area_search, tags_search, ingredients_search, vegetarian_filter, kosher_filter, margarine_for_butter, applesauce_for_oil, greek_yogurt_for_sour_cream, honey_for_sugar

def parse_singular_ingredients(sections):
    try:
        if isinstance(sections, str):
            sections = eval(sections)  # Convert string representation of list to actual list
        ingredients = set()
        display_ingredients = set()
        for section in sections:
            for component in section['components']:
                ingredient = component['ingredient']
                singular = ingredient['display_singular']
                plural = ingredient['display_plural']
                ingredients.add(singular)
                ingredients.add(plural)
                display_ingredients.add(singular)
        return ', '.join(display_ingredients), ', '.join(ingredients)
    except Exception as e:
        return '', ''

def parse_instructions(instructions):
    try:
        if isinstance(instructions, str):
            instructions = eval(instructions)  # Convert string representation of list to actual list
        instruction_texts = [f"{i+1}. {instruction['display_text']}" for i, instruction in enumerate(instructions)]
        return '\n'.join(instruction_texts)
    except Exception as e:
        return ''