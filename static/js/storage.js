/**
 * Clear Recipes - Storage module
 * Handles saving and retrieving recipes from server-side storage
 */

window.recipeStorage = (function() {

    /**
     * Get all saved recipes from server
     */
    async function getSavedRecipes() {
        try {
            const response = await fetch('/api/saved');
            const data = await response.json();
            return data.success ? data.recipes : [];
        } catch (e) {
            console.error('Error reading saved recipes:', e);
            return [];
        }
    }

    /**
     * Save a recipe to server
     */
    async function saveRecipe(recipe) {
        try {
            const response = await fetch('/api/saved', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: recipe.title,
                    serves: recipe.serves,
                    ingredients: recipe.ingredients,
                    steps: recipe.steps,
                    source_url: recipe.source_url || null,
                    notes: recipe.notes || null
                })
            });
            return await response.json();
        } catch (e) {
            console.error('Error saving recipe:', e);
            return { success: false, error: e.message };
        }
    }

    /**
     * Delete a saved recipe
     */
    async function deleteRecipe(recipeId) {
        try {
            const response = await fetch(`/api/saved/${recipeId}`, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (e) {
            console.error('Error deleting recipe:', e);
            return { success: false, error: e.message };
        }
    }

    /**
     * Get a single saved recipe by ID
     */
    async function getRecipe(recipeId) {
        try {
            const response = await fetch(`/api/saved/${recipeId}`);
            const data = await response.json();
            return data.success ? data.recipe : null;
        } catch (e) {
            console.error('Error getting recipe:', e);
            return null;
        }
    }

    /**
     * Check if a recipe is saved (by title)
     */
    async function isRecipeSaved(title) {
        const saved = await getSavedRecipes();
        return saved.some(r => r.title === title);
    }

    // Public API
    return {
        getSavedRecipes,
        saveRecipe,
        deleteRecipe,
        getRecipe,
        isRecipeSaved
    };
})();
