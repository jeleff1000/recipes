import pandas as pd

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def calculate_similarity(search_ingredients, search_meal, df):
    search_ingredients_set = set(filter(None, search_ingredients.lower().split(', ')))
    search_meal_set = set(search_meal.lower().split())

    def similarity(row):
        ingredients_set = set(filter(None, row['isolated_ingredients'].lower().split(', ')))
        meal_set = set(row['strMeal'].lower().split())
        ingredients_similarity = jaccard_similarity(search_ingredients_set, ingredients_set)
        meal_similarity = jaccard_similarity(search_meal_set, meal_set)
        return (2 * ingredients_similarity + meal_similarity) / 3

    df['similarity'] = df.apply(similarity, axis=1)
    return df

def find_top_similar_items(search_ingredients, search_meal, df):
    # Create a new DataFrame with the required columns
    df_strMeal_isolated_ingredients = df[['strMeal', 'isolated_ingredients', 'strMealThumb']].copy()

    # Calculate similarity on the new DataFrame
    df_with_similarity = calculate_similarity(search_ingredients, search_meal, df_strMeal_isolated_ingredients.copy())

    # Filter out the exact match
    df_filtered = df_with_similarity[
        (df_with_similarity['isolated_ingredients'].str.lower() != search_ingredients.lower()) |
        (df_with_similarity['strMeal'].str.lower() != search_meal.lower())
    ]

    top_items = df_filtered.nlargest(3, 'similarity')
    return top_items[['strMeal', 'strMealThumb', 'isolated_ingredients']]