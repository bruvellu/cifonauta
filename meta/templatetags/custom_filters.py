from django import template
from django.utils.safestring import mark_safe
from meta.models import Media

register = template.Library()

@register.filter
def get_value(obj, attr_name):
    if attr_name == "authors" or attr_name == "taxa":
        query = None

        if attr_name == "taxa":
            query = list(obj.taxa.all())
        else:
            query = getattr(obj, attr_name, '').all()

        html = "<ul>"
        for value in query:
            html += f"<li>{value.name}</li>"
        html += "</ul>"

        return mark_safe(html)
    
    if getattr(obj, attr_name, '') == None:
        return ""
    
    return getattr(obj, attr_name, '')