from django import template

register = template.Library()


@register.filter(is_safe=True)
def set_label_attrs(value, arg):
    return value.label_tag(attrs={'class': arg})
