from django import template
from django.utils.safestring import mark_safe
from meta.models import Curadoria

register = template.Library()


@register.simple_tag
def get_media_curations(media):
  taxons = media.taxa.all()
  curations = Curadoria.objects.filter(taxons__in=taxons).distinct()
  return list(curations)

  
@register.simple_tag
def get_field_value(obj, field_name):
  if field_name == "authors" or field_name == "taxa" or field_name == "tags":
    return list(getattr(obj, field_name, '').all())

  field = obj._meta.get_field(field_name)

  if field.choices:
    field_choices = dict(field.choices)
    key = getattr(obj, field_name, '')

    if key:
      return field_choices[key] 
    return ""
    
  if getattr(obj, field_name, '') == None:
    return ""

  return getattr(obj, field_name, '')