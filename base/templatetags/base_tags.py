from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name="to_int")
def to_int(value):
    try:
        return int(value)
    except ValueError:
        return value
    
@register.filter(name='has_group')
def has_group(user, group_name):
    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()
    return False


@register.simple_tag(takes_context=True)
def set_var(context, var_name, var_value):
    """
    Allows setting a context variable from inside a Django template.
    Usage example: {% set_var 'myvar' True %}
    """
    context[var_name] = var_value
    return ""