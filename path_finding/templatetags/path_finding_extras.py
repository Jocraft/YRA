from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def get_answer(saved_answers, question_number):
    """
    Template filter to get a saved answer for a question number.
    Usage: {{ saved_answers|get_answer:question_number }}
    """
    key = f'q{question_number}'
    return saved_answers.get(key, '') 