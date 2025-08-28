

from django import template
from django.forms.widgets import Widget

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    if isinstance(value, Widget):
        return value.as_widget(attrs={'class': arg})
    else:
        return value
