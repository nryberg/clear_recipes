/**
 * Clear Recipes - Timer module
 * Handles countdown timers for recipe steps
 */

window.recipeTimer = (function() {
    // Active timers
    const timers = {};

    /**
     * Create HTML for a timer
     */
    function createTimerHTML(timer, index) {
        return `
            <div class="timer bg-blue-50 dark:bg-blue-900 border-2 border-blue-300 dark:border-blue-700 rounded p-4 md:p-6" id="timer-${index}">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-lg md:text-xl font-semibold">Timer: ${timer.display}</h4>
                    <div class="timer-display text-2xl md:text-3xl font-mono font-bold" id="timer-display-${index}">
                        ${formatTime(timer.duration_seconds)}
                    </div>
                </div>
                <div class="flex gap-3">
                    <button
                        onclick="window.recipeTimer.startTimer(${index})"
                        id="timer-start-${index}"
                        class="flex-1 px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-600 transition font-medium"
                    >
                        Start
                    </button>
                    <button
                        onclick="window.recipeTimer.pauseTimer(${index})"
                        id="timer-pause-${index}"
                        class="flex-1 px-4 py-2 bg-gray-600 dark:bg-gray-500 text-white rounded hover:bg-gray-700 dark:hover:bg-gray-600 transition font-medium hidden"
                    >
                        Pause
                    </button>
                    <button
                        onclick="window.recipeTimer.resetTimer(${index})"
                        id="timer-reset-${index}"
                        class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded hover:bg-gray-400 dark:hover:bg-gray-500 transition font-medium"
                    >
                        Reset
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Initialize a timer
     */
    function initTimer(index, durationSeconds) {
        timers[index] = {
            duration: durationSeconds,
            remaining: durationSeconds,
            interval: null,
            running: false
        };
    }

    /**
     * Start a timer
     */
    function startTimer(index) {
        const timer = timers[index];
        if (!timer || timer.running) return;

        timer.running = true;

        // Update UI
        document.getElementById(`timer-start-${index}`).classList.add('hidden');
        document.getElementById(`timer-pause-${index}`).classList.remove('hidden');

        // Start countdown
        timer.interval = setInterval(() => {
            timer.remaining--;

            // Update display
            updateTimerDisplay(index);

            // Check if completed
            if (timer.remaining <= 0) {
                completeTimer(index);
            }
        }, 1000);
    }

    /**
     * Pause a timer
     */
    function pauseTimer(index) {
        const timer = timers[index];
        if (!timer || !timer.running) return;

        timer.running = false;
        clearInterval(timer.interval);

        // Update UI
        document.getElementById(`timer-start-${index}`).classList.remove('hidden');
        document.getElementById(`timer-pause-${index}`).classList.add('hidden');
    }

    /**
     * Reset a timer
     */
    function resetTimer(index) {
        const timer = timers[index];
        if (!timer) return;

        // Stop if running
        if (timer.running) {
            pauseTimer(index);
        }

        // Reset remaining time
        timer.remaining = timer.duration;

        // Update display
        updateTimerDisplay(index);

        // Remove completed state
        const timerElement = document.getElementById(`timer-${index}`);
        if (timerElement) {
            timerElement.classList.remove('bg-green-50', 'dark:bg-green-900', 'border-green-300', 'dark:border-green-700');
            timerElement.classList.add('bg-blue-50', 'dark:bg-blue-900', 'border-blue-300', 'dark:border-blue-700');
        }
    }

    /**
     * Complete a timer
     */
    function completeTimer(index) {
        const timer = timers[index];
        if (!timer) return;

        // Stop the timer
        timer.running = false;
        clearInterval(timer.interval);
        timer.remaining = 0;

        // Update display
        updateTimerDisplay(index);

        // Update UI to show completion
        const timerElement = document.getElementById(`timer-${index}`);
        if (timerElement) {
            timerElement.classList.remove('bg-blue-50', 'dark:bg-blue-900', 'border-blue-300', 'dark:border-blue-700');
            timerElement.classList.add('bg-green-50', 'dark:bg-green-900', 'border-green-300', 'dark:border-green-700');
        }

        document.getElementById(`timer-start-${index}`).classList.add('hidden');
        document.getElementById(`timer-pause-${index}`).classList.add('hidden');

        // Alert user (visual and audio)
        alert('Timer completed!');

        // Try to play a beep sound (if available)
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRQ0PVqzn77BdGAg+ltryxnMpBSl+zPLaizsIGGS57OihUBELTKXh8bllHAU2j9Xy0H0vBSh+zPDblEILElq16+mjWBUJQJzi8r1uHwU0iM/z1YU1Bx9uwO3mnU0NDlat6O+0XxkIPJrX8sR2KwUle8rx3Is+CRZftuzvpVMRClGn4vG8bCAFM4fP8tV/MAUmfsrw25dDCxNYs+rro1oXCUCb4PG/cSMGNYnP89SBMwcfa77r55xLDAw+ltjxyHQrBSh+yvDdk0ALElqy6umlVhMJQp/h8r5wIgU0hs/y1X8xBSZ+yvDbl0MLEliy6+qjWRUJP5vf8cBzJAU2is7y1H4xBx1qvu3mnEwMDFCp5O+yYBoHPJfW8sR3LAUmf8vw3I4+CRVdt+vppVYTCkCf4PK8bSEFM4fO8tWAMgUlf8rw3JZCCxJXsuvrplgVCT6b3/HAdCQFNojO8tWAMQcda73t5p1MDAxQqOPvsWEaBzyWlvLJdysEJ37K8N+RQAsQV7Hq66dYFQk/ndTyv3AhBTOHz/LUgjIGJH7K8NuWQwoSV7Hs66hZFQo9mtzyv3MkBjWIzvPUgDEHHWq+7eedTA0LT6nl77NgGgY9l5T')[0];
            audio.play();
        } catch (e) {
            // Ignore if audio playback fails
        }
    }

    /**
     * Update timer display
     */
    function updateTimerDisplay(index) {
        const timer = timers[index];
        if (!timer) return;

        const displayElement = document.getElementById(`timer-display-${index}`);
        if (displayElement) {
            displayElement.textContent = formatTime(timer.remaining);
        }
    }

    /**
     * Format seconds to MM:SS
     */
    function formatTime(seconds) {
        if (seconds <= 0) {
            return '00:00';
        }

        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${pad(minutes)}:${pad(secs)}`;
        } else {
            return `${pad(minutes)}:${pad(secs)}`;
        }
    }

    /**
     * Pad number with leading zero
     */
    function pad(num) {
        return num.toString().padStart(2, '0');
    }

    // Public API
    return {
        createTimerHTML,
        initTimer,
        startTimer,
        pauseTimer,
        resetTimer
    };
})();
