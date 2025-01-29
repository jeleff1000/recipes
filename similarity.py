import pandas as pd

def jaccard_similarity(list1, list2):
    set1, set2 = set(list1), set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def calculate_similarity(search_ingredients, df):
    search_set = set(filter(None, search_ingredients.lower().split(', ')))

    def similarity(ingredients):
        ingredients_set = set(filter(None, ingredients.lower().split(', ')))
        sim = jaccard_similarity(search_set, ingredients_set)
        return sim

    df['similarity'] = df['isolated_ingredients'].apply(similarity)
    return df

def find_top_similar_items(search_ingredients, df):
    # Create a new DataFrame with the required columns
    df_strMeal_isolated_ingredients = df[['strMeal', 'isolated_ingredients', 'strMealThumb']].copy()

    # Calculate similarity on the new DataFrame
    df_with_similarity = calculate_similarity(search_ingredients, df_strMeal_isolated_ingredients.copy())

    # Filter out the exact match
    df_filtered = df_with_similarity[df_with_similarity['isolated_ingredients'].str.lower() != search_ingredients.lower()]

    top_items = df_filtered.nlargest(3, 'similarity')
    return top_items[['strMeal', 'strMealThumb', 'isolated_ingredients']]