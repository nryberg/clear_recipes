"""
Recipe parser for plain text recipe files.
Parses recipes in the format used in samples/pancakes.txt
"""

import re
from typing import Dict, List


def parse_recipe(filepath: str) -> Dict:
    """
    Parse a recipe from a text file.

    Args:
        filepath: Path to the recipe text file

    Returns:
        Dictionary containing structured recipe data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return parse_recipe_text(content)


def parse_recipe_text(content: str) -> Dict:
    """
    Parse recipe content from text string.

    Args:
        content: Recipe text content

    Returns:
        Dictionary containing structured recipe data
    """
    lines = content.split('\n')

    # Extract title (first non-empty line)
    title = ""
    for line in lines:
        if line.strip():
            title = line.strip()
            break

    # Extract metadata (serves)
    serves = ""
    for line in lines:
        if line.lower().startswith("serves:"):
            serves = line.split(":", 1)[1].strip()
            break

    # Find ingredient section
    ingredients = []
    in_ingredients = False
    for line in lines:
        stripped = line.strip()

        if stripped.lower() == "ingredients:":
            in_ingredients = True
            continue

        if stripped.lower() == "instructions:":
            in_ingredients = False
            break

        if in_ingredients and stripped:
            ingredients.append(stripped)

    # Find notes section
    notes = None
    in_notes = False
    notes_lines = []
    for line in lines:
        stripped = line.strip()

        if stripped.lower() == "notes:":
            in_notes = True
            continue

        if in_notes and stripped.lower() in ["instructions:", "ingredients:"]:
            in_notes = False
            break

        if in_notes and stripped:
            notes_lines.append(stripped)

    if notes_lines:
        notes = '\n'.join(notes_lines)

    # Find instruction steps
    steps = []
    in_instructions = False
    current_step = None

    for line in lines:
        stripped = line.strip()

        if stripped.lower() == "instructions:":
            in_instructions = True
            continue

        if in_instructions:
            # Match numbered steps: "1. ", "2. ", etc.
            match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
            if match:
                # Save previous step if exists
                if current_step:
                    steps.append(current_step)

                # Start new step
                current_step = {
                    'number': int(match.group(1)),
                    'text': match.group(2),
                    'ingredients': [],
                    'timers': []
                }
            elif current_step and stripped:
                # Multi-line step continuation
                current_step['text'] += ' ' + stripped

    # Add the last step
    if current_step:
        steps.append(current_step)

    # Break steps into individual sentences
    sentence_steps = break_into_sentences(steps)

    return {
        'title': title,
        'serves': serves,
        'ingredients': ingredients,
        'steps': sentence_steps,
        'notes': notes
    }


def break_into_sentences(steps: List[Dict]) -> List[Dict]:
    """
    Break recipe steps into individual sentences.

    Args:
        steps: List of step dictionaries with 'text' field

    Returns:
        List of sentence-level steps
    """
    sentence_steps = []

    for step in steps:
        text = step['text']

        # Split by sentence boundaries (., !, ?)
        # Use regex to split but keep the punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                sentence_steps.append({
                    'number': len(sentence_steps) + 1,
                    'text': sentence,
                    'ingredients': [],
                    'timers': []
                })

    return sentence_steps


if __name__ == '__main__':
    # Test with pancakes recipe
    import os
    test_file = 'samples/pancakes.txt'
    if os.path.exists(test_file):
        recipe = parse_recipe(test_file)
        print(f"Title: {recipe['title']}")
        print(f"Serves: {recipe['serves']}")
        print(f"Ingredients: {len(recipe['ingredients'])}")
        print(f"Steps: {len(recipe['steps'])}")
        print("\nSteps:")
        for step in recipe['steps']:
            print(f"  {step['number']}. {step['text'][:50]}...")
