"""
Ingredient matcher for matching ingredients to recipe steps.
Uses smart matching with variations and stemming.
"""

import re
from typing import List, Set


# Common measurements and quantity words to remove
MEASUREMENTS = [
    'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'tbs',
    'teaspoon', 'teaspoons', 'tsp',
    'ounce', 'ounces', 'oz',
    'pound', 'pounds', 'lb', 'lbs',
    'gram', 'grams', 'g',
    'kilogram', 'kilograms', 'kg',
    'milliliter', 'milliliters', 'ml',
    'liter', 'liters', 'l',
    'of', 'the', 'a', 'an',
    'sifted', 'melted', 'unsalted', 'salted',
    'beaten', 'whisked', 'chopped', 'diced', 'minced',
    'fresh', 'dried', 'frozen',
    'large', 'medium', 'small',
    'whole', 'half', 'quarter'
]


def extract_ingredient_name(ingredient_line: str) -> str:
    """
    Extract the core ingredient name from a full ingredient string.

    Args:
        ingredient_line: Full ingredient string (e.g., "2 cups of flour")

    Returns:
        Core ingredient name (e.g., "flour")
    """
    # Remove leading quantities like "1", "2", "1/2", "1-2", "1 1/2"
    text = re.sub(r'^\d+[\s\/-]?\d*\/?\d*\s*', '', ingredient_line)

    # Remove measurements
    for measure in MEASUREMENTS:
        # Word boundary matching to avoid partial replacements
        text = re.sub(rf'\b{measure}\b', '', text, flags=re.IGNORECASE)

    # Split by comma and take first part (handles "eggs, beaten")
    text = text.split(',')[0].strip()

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def get_ingredient_variations(ingredient_name: str) -> Set[str]:
    """
    Generate variations of an ingredient name for matching.

    Args:
        ingredient_name: Core ingredient name

    Returns:
        Set of variations (singular, plural, stemmed forms)
    """
    variations = {ingredient_name.lower()}

    # Add singular/plural variations
    if ingredient_name.endswith('s') and len(ingredient_name) > 3:
        # Remove 's' for singular
        variations.add(ingredient_name[:-1].lower())
    else:
        # Add 's' for plural
        variations.add((ingredient_name + 's').lower())

    # Add variations without common endings
    if ingredient_name.lower().endswith('ed'):
        variations.add(ingredient_name[:-2].lower())
        variations.add(ingredient_name[:-1].lower())

    if ingredient_name.lower().endswith('ing'):
        variations.add(ingredient_name[:-3].lower())

    # For multi-word ingredients, only add the LAST word as a variation
    # The first words are usually modifiers (baking, brown, chocolate)
    # that could cause false matches (e.g., "baking" matching "baking sheets")
    words = ingredient_name.split()
    if len(words) > 1:
        last_word = words[-1]
        if len(last_word) > 3:
            variations.add(last_word.lower())

    return variations


def match_ingredients_to_step(step_text: str, ingredients: List[str]) -> List[str]:
    """
    Match ingredients from the full ingredient list to a specific step's text.

    Args:
        step_text: The instruction text for the step
        ingredients: List of all ingredient strings

    Returns:
        List of matched ingredient strings
    """
    matched = []
    step_lower = step_text.lower()

    for ingredient in ingredients:
        name = extract_ingredient_name(ingredient)

        # Skip empty names
        if not name:
            continue

        variations = get_ingredient_variations(name)

        # Check if any variation appears in the step text as a whole word
        for variant in variations:
            if variant and re.search(rf'\b{re.escape(variant)}\b', step_lower):
                matched.append(ingredient)
                break

    return matched


if __name__ == '__main__':
    # Test ingredient matching
    test_ingredients = [
        "1 teaspoon salt",
        "2 teaspoons baking powder",
        "1 teaspoon baking soda",
        "2 cups of sifted flour",
        "2 tablespoons sugar",
        "2 eggs, slightly whisked",
        "2 cups of buttermilk",
        "2 tablespoons butter, unsalted and melted"
    ]

    test_step = "In a medium bowl, whisk together the salt, baking powder, baking soda, flour and sugar."

    print("Testing ingredient matching:")
    print(f"\nStep: {test_step}\n")
    print("All ingredients:")
    for ing in test_ingredients:
        print(f"  - {ing}")

    matched = match_ingredients_to_step(test_step, test_ingredients)

    print(f"\nMatched ingredients ({len(matched)}):")
    for ing in matched:
        print(f"  - {ing}")
