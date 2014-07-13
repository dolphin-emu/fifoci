from django import template
from django.utils.safestring import mark_safe
import markdown as markdown_mod

register = template.Library()

@register.filter
def markdown(text):
    return mark_safe(markdown_mod.markdown(text))
