from django import template

register = template.Library()


@register.filter(name='format')
def format(value, fmt):
    if type(value) == str:
        return value
    return fmt.format(value)
