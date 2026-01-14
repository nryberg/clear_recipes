# Clear Recipes

Clear Recipes is a web application that displays recipes step-by-step with smart features for an optimal cooking experience. Navigate through recipe steps using swipe gestures or arrow keys, with automatically matched ingredients and detected timers for each step.

## Features

- **Step-by-Step Display**: One recipe step per page with maximum font sizes for easy reading
- **Smart Ingredient Matching**: Automatically shows only the ingredients needed for each step
- **Auto-Detected Timers**: Recognizes timing phrases like "5 minutes" or "1 hour" and creates countdown timers
- **Intuitive Navigation**:
  - Swipe left/right on mobile
  - Arrow keys (←/→) on desktop
  - Previous/Next buttons
- **Multiple Input Methods**:
  - Paste URLs from 100+ recipe websites (AllRecipes, Food Network, NYT Cooking, etc.)
  - Load local `.txt` recipe files
- **Clean Design**: Black text on white background with Tailwind CSS styling
- **Network Access**: Configurable port for access via Tailscale or local network

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nryberg/clear_recipes.git
cd clear_recipes
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

**Default port (5000):**
```bash
python app.py
```

**Custom port:**
```bash
python app.py --port 8080
```

**Using environment variable:**
```bash
export RECIPE_APP_PORT=8080
python app.py
```

**Debug mode:**
```bash
python app.py --debug
```

### Accessing the Application

- **Locally**: `http://localhost:5000`
- **Tailscale**: `http://<tailscale-hostname>:<port>`
- **Local Network**: `http://<local-ip>:<port>`

### Using the App

1. **Scrape from Web**:
   - Paste a recipe URL on the home page
   - Click "Load" to scrape and display the recipe
   - Example URL: https://ohsweetbasil.com/melt-in-your-mouth-buttermilk-pancakes-recipe/

2. **Load Local Recipe**:
   - Add `.txt` files to the `recipes/` directory
   - Click on a recipe from the home page list

3. **Navigate Steps**:
   - Use arrow keys (←/→) on keyboard
   - Swipe left/right on touch devices
   - Click Previous/Next buttons

4. **Use Timers**:
   - Timers are automatically detected and displayed
   - Click "Start" to begin countdown
   - Click "Pause" to pause
   - Click "Reset" to reset to original duration

## Recipe Text File Format

Create local recipe files in the `recipes/` directory with this format:

```
Recipe Title

Serves: 4 servings

Ingredients:
1 cup flour
2 eggs
1 teaspoon salt

Instructions:
1. First step of the recipe.
2. Second step with more details.
3. Third step mentioning specific ingredients.
```

## Project Structure

```
clear_recipes/
├── app.py                    # Flask application
├── recipe_parser.py          # Parse text file recipes
├── recipe_scraper.py         # Scrape web recipes
├── ingredient_matcher.py     # Match ingredients to steps
├── timer_detector.py         # Detect timing phrases
├── requirements.txt          # Python dependencies
├── recipes/                  # Local recipe files
│   └── pancakes.txt
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html
│   └── recipe.html
└── static/
    └── js/                   # JavaScript modules
        ├── app.js            # SPA logic
        ├── navigation.js     # Keyboard & swipe
        └── timer.js          # Timer functionality
```

## Supported Recipe Websites

The app uses the `recipe-scrapers` library which supports 100+ websites including:

- AllRecipes
- Food Network
- NYT Cooking
- Serious Eats
- Bon Appétit
- Tasty
- BBC Food
- And many more!

## Development

### Running Tests

Test individual components:
```bash
python recipe_parser.py      # Test recipe parsing
python ingredient_matcher.py # Test ingredient matching
python timer_detector.py     # Test timer detection
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request. 
