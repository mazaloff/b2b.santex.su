from django import template
import re

register = template.Library()


@register.filter(name='format')
def format(value, fmt):
    if type(value) == str:
        return value
    elif value > 1000:
        return re.sub(r'(?<=\d)(?=(\d\d\d)+\b)', ' ', str(fmt.format(value)))
    else:
        return str(fmt.format(value))


@register.filter(name='units')
def units(value):
    if type(value) == str:
        return value + ' штук'
    elif value == 1:
        return str(value) + " штука"
    elif value <= 4:
        return str(value) + " штуки"
    else:
        return str(value) + " штук"


@register.filter(name='currency')
def currency(value, currency):
    return str(value) + " " + str(currency)
