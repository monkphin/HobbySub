"""
Utility functions for common tasks across the project.

Includes helpers for:
- Flash messages (alert)


Import and use these anywhere you need a reusable function that keeps views clean and DRY.
"""

from django.contrib import messages

def alert(request, level, msg):
    """
    Flash a message to the user at the specified level using Django's messages framework.

    Args:
        request: The HttpRequest object.
        level (str): One of 'success', 'info', 'warning', 'error'.
        msg (str): The message text to display.

    Defaults to 'info' if an invalid level is given.
    """
    # Get the correct message function based on the level, defaulting to `info`
    message_func = {
        "success": messages.success,
        "info": messages.info,
        "warning": messages.warning,
        "error": messages.error
    }.get(level, messages.info)

    # Call the selected message function with the request and msg
    message_func(request, msg)
