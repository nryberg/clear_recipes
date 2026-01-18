# Clear Recipes Chrome Extension

Send any recipe page to Clear Recipes with one click.

## Installation (Developer Mode)

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select this `chrome-extension` folder
5. The extension icon appears in your toolbar!

## Usage

1. Navigate to any recipe page (AllRecipes, Food Network, NYT Cooking, etc.)
2. Click the Clear Recipes extension icon
3. The recipe loads in Clear Recipes automatically

## Icons

You'll need to add icon files:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

You can create simple icons at https://favicon.io/ or use any image editor.

## Customization

Edit `background.js` to change the Clear Recipes URL if needed:
```javascript
const CLEAR_RECIPES_URL = 'https://recipes.rybergs.com';
```
