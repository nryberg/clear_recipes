"""
Clear Recipes - Flask application
A web app for displaying recipes step-by-step with smart features.
"""

from flask import Flask, render_template, jsonify, request
import os
import argparse
from recipe_parser import parse_recipe
from recipe_scraper import scrape_recipe
from ingredient_matcher import match_ingredients_to_step
from timer_detector import detect_timers

app = Flask(__name__)

# Directory for local recipes
RECIPES_DIR = 'recipes'


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

        # Process each step: match ingredients and detect timers
        all_ingredients = recipe_data['ingredients']

        for step in recipe_data['steps']:
            # Match ingredients to this step
            step['ingredients'] = match_ingredients_to_step(step['text'], all_ingredients)

            # Detect timers in this step
            step['timers'] = detect_timers(step['text'])

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

        # Process each step: match ingredients and detect timers
        all_ingredients = recipe_data['ingredients']

        for step in recipe_data['steps']:
            # Match ingredients to this step
            step['ingredients'] = match_ingredients_to_step(step['text'], all_ingredients)

            # Detect timers in this step
            step['timers'] = detect_timers(step['text'])

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
