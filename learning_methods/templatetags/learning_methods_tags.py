from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key
    that might need to be converted to string
    """
    if not dictionary:
        return []
    
    # Convert the key to the format used in the dictionary
    dict_key = f'q{key}'
    
    # Get the value and split it into a list
    value = dictionary.get(dict_key, '')
    return value.split(',') if value else [] 