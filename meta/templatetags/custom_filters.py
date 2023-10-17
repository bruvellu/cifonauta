from django import template
from django.utils.safestring import mark_safe
from meta.models import Media

register = template.Library()

@register.filter
def get_value(obj, attr_name):
    if attr_name == "co_author" or attr_name == "taxons":
        query = None

        # Needs this conditional because taxons is a field from ModifiedMedia, but not from Media
        if attr_name == "taxons":
            if isinstance(obj, Media):
                query = list(obj.taxon_set.all())
            else:
                query = list(obj.taxons.all())
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