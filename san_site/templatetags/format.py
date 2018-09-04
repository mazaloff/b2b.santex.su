from django import template

register = template.Library()


@register.filter(name='format')
def format(value, fmt):
    if type(value) == str:
        return value
    return fmt.format(value)


@register.filter(name='units')
def units(value):
    if value == 1:
        return str(value) + " штука "
    elif value <= 4:
        return str(value) + " штуки "
    else:
        return str(value) + " штук "
