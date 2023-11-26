from django import template
from django.utils.safestring import mark_safe
from meta.models import Curadoria

register = template.Library()

@register.filter
def get_attribute(obj, attr_name):
    if attr_name == "authors" or attr_name == "taxa":
        query = getattr(obj, attr_name, '').all()

        html = "<ul>"
        for value in query:
            html += f"<li>{value.name}</li>"
        html += "</ul>"

        return mark_safe(html)
    
    field = obj._meta.get_field(attr_name)

    if field.choices:
        field_choices = dict(field.choices)
        key = getattr(obj, attr_name, '')
        return field_choices[key]
    
    if getattr(obj, attr_name, '') == None:
        return ""

    return getattr(obj, attr_name, '')

@register.simple_tag
def get_media_curations(media):
  taxons = media.taxa.all()
  curations = Curadoria.objects.filter(taxons__in=taxons).distinct()
  return list(curations)