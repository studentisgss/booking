from django import template
import markdown as _markdown
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter(is_safe=True)
def markdown(value, arg=None):
    """ Render markdown over a given value.
    Syntax: ::
        {{value|markdown}}
    :returns: A rendered markdown
    """
    return mark_safe(_markdown.markdown(escape(value)))
