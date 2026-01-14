/**
 * Clear Recipes - Main SPA functionality
 * Handles recipe loading, step rendering, and state management
 */

window.recipeViewer = (function() {
    // State
    let recipe = null;
    let currentStepIndex = 0;

    // DOM elements
    let elements = {};

    /**
     * Initialize the recipe viewer
     */
    function init(recipeId) {
        // Get DOM elements
        elements = {
            recipeTitle: document.getElementById('recipe-title'),
            recipeServes: document.getElementById('recipe-serves'),
            stepIngredients: document.getElementById('step-ingredients'),
            stepInstruction: document.getElementById('step-instruction'),
            stepTimers: document.getElementById('step-timers'),
            stepIndicator: document.getElementById('step-indicator'),
            prevBtn: document.getElementById('prev-btn'),
            nextBtn: document.getElementById('next-btn'),
            loadingState: document.getElementById('loading-state'),
            errorState: document.getElementById('error-state'),
            errorMessage: document.getElementById('error-message'),
            recipeContainer: document.getElementById('recipe-container')
        };

        // Load recipe
        loadRecipe(recipeId);

        // Initialize navigation
        if (window.recipeNavigation) {
            window.recipeNavigation.init({
                onNext: nextStep,
                onPrev: previousStep
            });
        }

        // Handle browser back/forward
        window.addEventListener('popstate', handlePopState);
    }

    /**
     * Load recipe data
     */
    async function loadRecipe(recipeId) {
        try {
            let recipeData;

            // Check if this is a scraped recipe
            if (recipeId === 'scraped') {
                const storedRecipe = sessionStorage.getItem('scraped-recipe');
                if (!storedRecipe) {
                    throw new Error('No scraped recipe found. Please return to home and try again.');
                }
                recipeData = JSON.parse(storedRecipe);
            } else {
                // Load from API
                const response = await fetch(`/api/recipe/${recipeId}`);
                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.error || 'Failed to load recipe');
                }

                recipeData = data.recipe;
            }

            // Store recipe
            recipe = recipeData;

            // Hide loading, show content
            elements.loadingState.style.display = 'none';
            elements.recipeContainer.style.visibility = 'visible';

            // Set recipe header
            elements.recipeTitle.textContent = recipe.title;
            elements.recipeServes.textContent = recipe.serves ? `Serves: ${recipe.serves}` : '';

            // Check for URL hash (e.g., #step-2)
            const hash = window.location.hash;
            if (hash && hash.startsWith('#step-')) {
                const stepNum = parseInt(hash.replace('#step-', ''));
                if (stepNum > 0 && stepNum <= recipe.steps.length) {
                    currentStepIndex = stepNum - 1;
                }
            }

            // Render first (or specified) step
            renderStep(currentStepIndex);

        } catch (error) {
            console.error('Error loading recipe:', error);
            showError(error.message);
        }
    }

    /**
     * Render a specific step
     */
    function renderStep(index) {
        if (!recipe || !recipe.steps || index < 0 || index >= recipe.steps.length) {
            return;
        }

        const step = recipe.steps[index];

        // Render ingredients for this step
        if (step.ingredients && step.ingredients.length > 0) {
            elements.stepIngredients.innerHTML = `
                <div class="bg-gray-100 dark:bg-gray-800 p-4 md:p-6 rounded">
                    <h3 class="text-xl md:text-2xl font-semibold mb-3">Ingredients for this step:</h3>
                    <ul class="space-y-2">
                        ${step.ingredients.map(ing => `
                            <li class="text-lg md:text-xl">${ing}</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        } else {
            elements.stepIngredients.innerHTML = '';
        }

        // Render instruction with dynamic font sizing
        const fontSize = calculateFontSize(step.text.length);
        elements.stepInstruction.className = `leading-relaxed ${fontSize}`;
        elements.stepInstruction.textContent = step.text;

        // Render timers
        if (step.timers && step.timers.length > 0) {
            elements.stepTimers.innerHTML = step.timers.map((timer, i) => `
                <div class="timer-container" data-timer-index="${i}">
                    ${window.recipeTimer ? window.recipeTimer.createTimerHTML(timer, i) : ''}
                </div>
            `).join('');

            // Initialize timers
            if (window.recipeTimer) {
                step.timers.forEach((timer, i) => {
                    window.recipeTimer.initTimer(i, timer.duration_seconds);
                });
            }
        } else {
            elements.stepTimers.innerHTML = '';
        }

        // Update step indicator
        elements.stepIndicator.textContent = `Step ${index + 1} of ${recipe.steps.length}`;

        // Update navigation buttons
        elements.prevBtn.disabled = index === 0;
        elements.nextBtn.disabled = index === recipe.steps.length - 1;

        // Update URL hash
        updateURLHash(index + 1);

        // Update navigation state
        if (window.recipeNavigation) {
            window.recipeNavigation.updateState({
                currentStep: index,
                totalSteps: recipe.steps.length
            });
        }
    }

    /**
     * Calculate font size based on text length
     */
    function calculateFontSize(textLength) {
        if (textLength < 50) return 'text-5xl md:text-7xl lg:text-8xl';
        if (textLength < 100) return 'text-4xl md:text-6xl lg:text-7xl';
        if (textLength < 150) return 'text-3xl md:text-5xl lg:text-6xl';
        if (textLength < 250) return 'text-2xl md:text-4xl lg:text-5xl';
        return 'text-xl md:text-3xl lg:text-4xl';
    }

    /**
     * Navigate to next step
     */
    function nextStep() {
        if (currentStepIndex < recipe.steps.length - 1) {
            currentStepIndex++;
            renderStep(currentStepIndex);
        }
    }

    /**
     * Navigate to previous step
     */
    function previousStep() {
        if (currentStepIndex > 0) {
            currentStepIndex--;
            renderStep(currentStepIndex);
        }
    }

    /**
     * Update URL hash for deep linking
     */
    function updateURLHash(stepNumber) {
        const newHash = `#step-${stepNumber}`;
        if (window.location.hash !== newHash) {
            history.pushState({ step: stepNumber }, '', newHash);
        }
    }

    /**
     * Handle browser back/forward buttons
     */
    function handlePopState(event) {
        if (event.state && event.state.step) {
            currentStepIndex = event.state.step - 1;
            renderStep(currentStepIndex);
        }
    }

    /**
     * Show error message
     */
    function showError(message) {
        elements.loadingState.style.display = 'none';
        elements.errorMessage.textContent = message;
        elements.errorState.classList.remove('hidden');
    }

    // Public API
    return {
        init,
        nextStep,
        previousStep
    };
})();
