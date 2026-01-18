// Clear Recipes Chrome Extension
const CLEAR_RECIPES_URL = 'https://recipes.rybergs.com';

chrome.action.onClicked.addListener((tab) => {
  if (tab.url) {
    const recipeUrl = encodeURIComponent(tab.url);
    chrome.tabs.update(tab.id, {
      url: `${CLEAR_RECIPES_URL}/?url=${recipeUrl}`
    });
  }
});
