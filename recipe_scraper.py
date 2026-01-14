"""
Recipe scraper for extracting recipes from URLs.
Uses the recipe-scrapers library which supports 100+ recipe websites.
"""

from recipe_scrapers import scrape_me
from typing import Dict, List
import re


def scrape_recipe(url: str) -> Dict:
    """
    Scrape a recipe from a URL using recipe-scrapers library.

    Args:
        url: URL of the recipe page

    Returns:
        Dictionary containing structured recipe data compatible with our format

    Raises:
        Exception: If scraping fails or URL is not supported
    """
    try:
        scraper = scrape_me(url, wild_mode=True)

        # Get basic recipe information
        title = scraper.title()
        yields = scraper.yields()
        ingredients = scraper.ingredients()
        instructions_text = scraper.instructions()

        # Parse instructions into numbered steps
        steps = parse_instructions(instructions_text)

        # Get timing information if available
        prep_time = None
        cook_time = None
        total_time = None

        try:
            prep_time = scraper.prep_time()
        except:
            pass

        try:
            cook_time = scraper.cook_time()
        except:
            pass

        try:
            total_time = scraper.total_time()
        except:
            pass

        return {
            'title': title,
            'serves': yields,
            'ingredients': ingredients,
            'steps': steps,
            'source_url': url,
            'prep_time': prep_time,
            'cook_time': cook_time,
            'total_time': total_time
        }

    except Exception as e:
        raise Exception(f"Failed to scrape recipe from {url}: {str(e)}")


def parse_instructions(instructions_text: str) -> List[Dict]:
    """
    Parse instruction text into numbered steps.

    Args:
        instructions_text: Raw instruction text from scraper

    Returns:
        List of step dictionaries
    """
    steps = []

    # Split by newlines first
    lines = instructions_text.split('\n')

    current_step = None
    step_number = 1

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Try to match numbered steps (1., 2., Step 1:, etc.)
        numbered_match = re.match(r'^(?:Step\s+)?(\d+)[\.\:\)]\s*(.+)$', stripped, re.IGNORECASE)

        if numbered_match:
            # Save previous step
            if current_step:
                steps.append(current_step)

            # Start new step
            step_number = int(numbered_match.group(1))
            current_step = {
                'number': step_number,
                'text': numbered_match.group(2),
                'ingredients': [],
                'timers': []
            }
        elif current_step:
            # Continuation of current step
            current_step['text'] += ' ' + stripped
        else:
            # No numbered format found - treat each paragraph as a step
            current_step = {
                'number': step_number,
                'text': stripped,
                'ingredients': [],
                'timers': []
            }
            steps.append(current_step)
            current_step = None
            step_number += 1

    # Add the last step if exists
    if current_step:
        steps.append(current_step)

    # If no steps were parsed (no numbered format), split by sentences/paragraphs
    if not steps:
        paragraphs = re.split(r'\n\n+', instructions_text)
        for i, paragraph in enumerate(paragraphs, 1):
            if paragraph.strip():
                steps.append({
                    'number': i,
                    'text': paragraph.strip(),
                    'ingredients': [],
                    'timers': []
                })

    return steps


if __name__ == '__main__':
    # Test with a sample URL (uncomment to test with a real URL)
    # url = "https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/"
    # recipe = scrape_recipe(url)
    # print(f"Title: {recipe['title']}")
    # print(f"Serves: {recipe['serves']}")
    # print(f"Ingredients: {len(recipe['ingredients'])}")
    # print(f"Steps: {len(recipe['steps'])}")

    print("Recipe scraper module ready.")
    print("Import and use scrape_recipe(url) to scrape recipes from the web.")
