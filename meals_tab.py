import streamlit as st
from utils import search_bar

def display_meals_tab(meals_df, combined_categories):
    st.title('Meals Data')

    # Use the centralized search bar with a unique prefix
    search_results = search_bar(meals_df, combined_categories, prefix='meals_')
    meal_search, category_search, area_search, tags_search, ingredients_search, vegetarian_filter, kosher_filter, margarine_for_butter, applesauce_for_oil, greek_yogurt_for_sour_cream, honey_for_sugar = search_results

    # Check if any search or filter values are provided
    if meal_search or category_search or area_search or tags_search or ingredients_search or vegetarian_filter or kosher_filter:
        # Filter the DataFrame based on the search terms
        if meal_search:
            meals_df = meals_df[meals_df['strMeal'].str.contains(meal_search, case=False, na=False)]
        if category_search:
            meals_df = meals_df[meals_df['strTags'].str.contains(category_search, case=False, na=False)]
        if area_search:
            meals_df = meals_df[meals_df['strTags'].str.contains(area_search, case=False, na=False)]
        if tags_search:
            tags = tags_search.split()
            for tag in tags:
                meals_df = meals_df[meals_df['strTags'].str.contains(tag, case=False, na=False)]
        if ingredients_search:
            ingredients = re.findall(r'"(.*?)"|(\S+)', ingredients_search)
            ingredients = [item[0] or item[1] for item in ingredients]
            for ingredient in ingredients:
                if ' ' in ingredient:
                    meals_df = meals_df[meals_df['ingredients'].str.contains(re.escape(ingredient), case=False, na=False)]
                else:
                    meals_df = meals_df[meals_df['ingredients'].str.contains(ingredient, case=False, na=False)]
        if vegetarian_filter:
            meals_df = meals_df[meals_df['strTags'].str.contains('Vegetarian', case=False, na=False)]
        if kosher_filter:
            meals_df = meals_df[~meals_df['ingredients'].str.contains('shrimp|pork', case=False, na=False)]
            meals_df = meals_df[~((meals_df['ingredients'].str.contains('meat|beef|lamb|chicken', case=False, na=False)) & (meals_df['ingredients'].str.contains('milk|cheese|yogurt|butter|sour cream', case=False, na=False)))]

        # Sort the DataFrame alphabetically by 'strMeal'
        meals_df = meals_df.sort_values(by='strMeal', ascending=True)

        # Display the DataFrame
        for index, row in meals_df.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("<br><br>", unsafe_allow_html=True)  # Add vertical space above the image
                st.image(row['strMealThumb'], caption=row['strMeal'], use_container_width=True)
            with col2:
                st.subheader(row['strMeal'])
                with st.expander("Instructions"):
                    st.write(row['strInstructions'])
                st.write(f"**Source:** {row['strSource']}")
                if 'strYoutube' in row and row['strYoutube']:
                    with st.expander("Video"):
                        st.video(row['strYoutube'])
                st.write(f"**Ingredients:** {row['ingredients']}")
    else:
        st.write("Please enter search criteria to display results.")