from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return value / arg
    except (ZeroDivisionError, TypeError, ValueError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0
