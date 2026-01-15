/**
 * Clear Recipes - Navigation module
 * Handles keyboard arrow keys and swipe gestures for step navigation
 */

window.recipeNavigation = (function() {
    // State
    let state = {
        currentStep: 0,
        totalSteps: 0
    };

    // Callbacks
    let callbacks = {
        onNext: null,
        onPrev: null
    };

    // Touch state for swipe detection
    let touchStartX = 0;
    let touchEndX = 0;
    let touchStartY = 0;
    let touchEndY = 0;

    // Constants
    const SWIPE_THRESHOLD = 50; // Minimum distance for a swipe (pixels)
    const VERTICAL_THRESHOLD = 30; // Maximum vertical movement for horizontal swipe

    /**
     * Initialize navigation
     */
    function init(options) {
        callbacks.onNext = options.onNext;
        callbacks.onPrev = options.onPrev;

        // Keyboard navigation
        document.addEventListener('keydown', handleKeyPress);

        // Touch navigation (swipe)
        document.addEventListener('touchstart', handleTouchStart, { passive: true });
        document.addEventListener('touchend', handleTouchEnd, { passive: true });

        // Button navigation
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (callbacks.onPrev && state.currentStep > 0) {
                    callbacks.onPrev();
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (callbacks.onNext && state.currentStep < state.totalSteps - 1) {
                    callbacks.onNext();
                }
            });
        }
    }

    /**
     * Handle keyboard arrow keys
     */
    function handleKeyPress(event) {
        switch(event.key) {
            case 'ArrowLeft':
                event.preventDefault();
                if (callbacks.onPrev && state.currentStep > 0) {
                    callbacks.onPrev();
                }
                break;

            case 'ArrowRight':
                event.preventDefault();
                if (callbacks.onNext && state.currentStep < state.totalSteps - 1) {
                    callbacks.onNext();
                }
                break;
        }
    }

    /**
     * Handle touch start (for swipe detection)
     */
    function handleTouchStart(event) {
        touchStartX = event.touches[0].clientX;
        touchStartY = event.touches[0].clientY;
    }

    /**
     * Handle touch end (for swipe detection)
     */
    function handleTouchEnd(event) {
        touchEndX = event.changedTouches[0].clientX;
        touchEndY = event.changedTouches[0].clientY;

        handleSwipe();
    }

    /**
     * Detect and handle swipe gesture
     */
    function handleSwipe() {
        const horizontalDiff = touchStartX - touchEndX;
        const verticalDiff = Math.abs(touchStartY - touchEndY);

        // Check if this is a horizontal swipe (not vertical scroll)
        if (verticalDiff > VERTICAL_THRESHOLD) {
            // Too much vertical movement - probably scrolling
            return;
        }

        // Check if swipe distance exceeds threshold
        if (Math.abs(horizontalDiff) > SWIPE_THRESHOLD) {
            if (horizontalDiff > 0) {
                // Swipe left - go to next step
                if (callbacks.onNext && state.currentStep < state.totalSteps - 1) {
                    callbacks.onNext();
                }
            } else {
                // Swipe right - go to previous step or home if at first step
                if (state.currentStep === 0) {
                    // At first step - go to home page
                    window.location.href = '/';
                } else if (callbacks.onPrev) {
                    callbacks.onPrev();
                }
            }
        }
    }

    /**
     * Update navigation state
     */
    function updateState(newState) {
        state = { ...state, ...newState };
    }

    // Public API
    return {
        init,
        updateState
    };
})();
