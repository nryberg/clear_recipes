"""
Timer detector for finding timing information in recipe steps.
Detects phrases like "5 minutes", "1 hour", "30 seconds" and converts to seconds.
"""

import re
from typing import List, Dict


def detect_timers(step_text: str) -> List[Dict]:
    """
    Detect timing information in a recipe step.

    Args:
        step_text: The instruction text for the step

    Returns:
        List of timer dictionaries with text, duration_seconds, and display
    """
    timers = []

    # Patterns for matching time durations
    # Format: (pattern, multiplier_in_seconds)
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(hours?|hrs?)', 3600),  # "1-2 hours"
        (r'(\d+(?:\.\d+)?)\s*(hours?|hrs?)', 3600),  # "2 hours"
        (r'(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(minutes?|mins?)', 60),  # "5-10 minutes"
        (r'(\d+(?:\.\d+)?)\s*(minutes?|mins?)', 60),  # "5 minutes"
        (r'(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(seconds?|secs?)', 1),  # "30-45 seconds"
        (r'(\d+(?:\.\d+)?)\s*(seconds?|secs?)', 1),  # "30 seconds"
    ]

    for pattern, multiplier in patterns:
        matches = re.finditer(pattern, step_text, re.IGNORECASE)
        for match in matches:
            # Check if it's a range (e.g., "5-10 minutes")
            if len(match.groups()) > 2 and match.group(2) and match.group(2)[0].isdigit():
                # Range detected - use the average
                num1 = float(match.group(1))
                num2 = float(match.group(2))
                duration = int((num1 + num2) / 2 * multiplier)
            else:
                # Single value
                num = float(match.group(1))
                duration = int(num * multiplier)

            timers.append({
                'text': match.group(0),
                'duration_seconds': duration,
                'display': format_duration(duration)
            })

    return timers


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "5 minutes", "1 hour 30 minutes")
    """
    if seconds >= 3600:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60

        if remaining_minutes > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minute{'s' if remaining_minutes > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''}"

    elif seconds >= 60:
        minutes = seconds // 60
        remaining_seconds = seconds % 60

        if remaining_seconds > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} {remaining_seconds} second{'s' if remaining_seconds > 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes > 1 else ''}"

    else:
        return f"{seconds} second{'s' if seconds != 1 else ''}"


if __name__ == '__main__':
    # Test timer detection
    test_steps = [
        "Preheat oven to 350°F for 10 minutes.",
        "Bake for 25-30 minutes until golden brown.",
        "Let it rest for 5 mins before serving.",
        "Cook for 1 hour and 30 minutes.",
        "Simmer for 2 hours.",
        "Microwave for 45 seconds.",
        "Wait until bubbles form (no specific time)."
    ]

    print("Testing timer detection:\n")
    for step in test_steps:
        timers = detect_timers(step)
        print(f"Step: {step}")
        if timers:
            for timer in timers:
                print(f"  ⏱️  {timer['text']} → {timer['display']} ({timer['duration_seconds']}s)")
        else:
            print(f"  No timers detected")
        print()
