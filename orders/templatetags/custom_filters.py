"""
Custom template filters for the orders app.

Includes:
- get_item: safely retrieve a dictionary value by key in templates.
"""


from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Retrieves a value from a dictionary by key.

    Args:
        dictionary (dict): The dictionary to search.
        key: The key to look up.

    Returns:
        The value for the given key, or None if the key does not exist.
    """
    return dictionary.get(key)
