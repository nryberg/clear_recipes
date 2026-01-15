"""
Clear Recipes - Flask application
A web app for displaying recipes step-by-step with smart features.
"""

from flask import Flask, render_template, jsonify, request
import os
import re
import argparse
from recipe_parser import parse_recipe
from recipe_scraper import scrape_recipe
from ingredient_matcher import match_ingredients_to_step
from timer_detector import detect_timers


def detect_preheat_oven(steps):
    """
    Scan steps for preheat oven instructions.
    Returns a list of preheat instructions found (e.g., "Preheat oven to 350°F").
    """
    preheat_pattern = re.compile(
        r'preheat\s+(?:the\s+)?oven\s+to\s+(\d+)\s*°?\s*(F|C|fahrenheit|celsius)?',
        re.IGNORECASE
    )

    preheat_instructions = []
    for step in steps:
        text = step.get('text', '')
        match = preheat_pattern.search(text)
        if match:
            temp = match.group(1)
            unit = match.group(2) or 'F'
            # Normalize unit
            if unit.lower() in ['c', 'celsius']:
                unit = '°C'
            else:
                unit = '°F'
            preheat_instructions.append(f"Preheat oven to {temp}{unit}")

    return preheat_instructions

app = Flask(__name__)

# Directory for local recipes
RECIPES_DIR = 'recipes'


def process_recipe_steps(recipe_data):
    """
    Process recipe steps:
    1. Add initial step with all ingredients
    2. Match ingredients to each step
    3. Carry over ingredients if step has none
    4. Detect timers
    """
    all_ingredients = recipe_data['ingredients']
    steps = recipe_data['steps']

    # Detect preheat oven instructions
    preheat_instructions = detect_preheat_oven(steps)

    # Create initial "ingredients" step
    ingredients_step = {
        'number': 0,
        'text': 'Gather these ingredients:',
        'ingredients': all_ingredients,
        'timers': [],
        'is_ingredients_list': True,
        'preheat': preheat_instructions
    }

    # Process each instruction step
    processed_steps = [ingredients_step]

    # Add notes page if recipe has notes
    notes = recipe_data.get('notes')
    if notes:
        notes_step = {
            'number': len(processed_steps),
            'text': notes,
            'ingredients': [],
            'timers': [],
            'is_notes_page': True
        }
        processed_steps.append(notes_step)

    for step in steps:
        # Match ingredients to this step
        step['ingredients'] = match_ingredients_to_step(step['text'], all_ingredients)

        # Detect timers in this step
        step['timers'] = detect_timers(step['text'])

        # Renumber
        step['number'] = len(processed_steps)
        processed_steps.append(step)

    # Add final "Bon Appetit!" page
    final_step = {
        'number': len(processed_steps),
        'text': 'Bon Appetit!',
        'ingredients': [],
        'timers': [],
        'is_final_page': True
    }
    processed_steps.append(final_step)

    recipe_data['steps'] = processed_steps
    return recipe_data


@app.route('/')
def index():
    """Home page - recipe selection and URL input."""
    return render_template('index.html')


@app.route('/recipe/<recipe_id>')
def recipe_viewer(recipe_id):
    """Recipe viewer page (SPA container)."""
    return render_template('recipe.html', recipe_id=recipe_id)


@app.route('/api/recipes')
def list_recipes():
    """List all available local recipes."""
    try:
        recipes = []
        if os.path.exists(RECIPES_DIR):
            for filename in os.listdir(RECIPES_DIR):
                if filename.endswith('.txt'):
                    recipe_id = filename[:-4]  # Remove .txt extension
                    recipes.append({
                        'id': recipe_id,
                        'name': recipe_id.replace('_', ' ').title()
                    })

        return jsonify({
            'success': True,
            'recipes': recipes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recipe/<recipe_id>')
def get_recipe(recipe_id):
    """Get a local recipe by ID."""
    try:
        # Build file path
        filepath = os.path.join(RECIPES_DIR, f"{recipe_id}.txt")

        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': f"Recipe '{recipe_id}' not found"
            }), 404

        # Parse the recipe
        recipe_data = parse_recipe(filepath)

        # Process steps: add ingredients list, match ingredients, carry over, detect timers
        recipe_data = process_recipe_steps(recipe_data)

        return jsonify({
            'success': True,
            'recipe': recipe_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recipe/scrape', methods=['POST'])
def scrape_recipe_endpoint():
    """Scrape a recipe from a URL."""
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        url = data['url']

        # Scrape the recipe
        recipe_data = scrape_recipe(url)

        # Process steps: add ingredients list, match ingredients, carry over, detect timers
        recipe_data = process_recipe_steps(recipe_data)

        return jsonify({
            'success': True,
            'recipe': recipe_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Clear Recipes Web Application')
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('RECIPE_APP_PORT', 5000)),
        help='Port to run the application on (default: 5000 or RECIPE_APP_PORT env var)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )

    args = parser.parse_args()

    print(f"Starting Clear Recipes on port {args.port}")
    print(f"Access the app at: http://localhost:{args.port}")
    print(f"For Tailscale access, use: http://<tailscale-hostname>:{args.port}")

    # Run the app
    app.run(
        host='0.0.0.0',  # Allow external connections (for Tailscale)
        port=args.port,
        debug=args.debug
    )
