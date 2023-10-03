from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_value(obj, attr_name):
    if attr_name == "co_author" or attr_name == "taxons":
        query = getattr(obj, attr_name, '').all()

        html = "<ul>"
        for value in query:
            html += f"<li>{value.name}</li>"
        html += "</ul>"

        return mark_safe(html)
    
    if getattr(obj, attr_name, '') == None:
        return ""
    
    return getattr(obj, attr_name, '')