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
  if field_name == "authors" or field_name == "taxa" or field_name == "tags" or field_name == 'references':
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


@register.simple_tag
def get_action_field(form, field_name):
    if field_name[-7:] != '_action':
        return { "is_action": False }
    
    has_field = field_name[:-7] in form.fields.keys()

    field = {
        "is_action": True,
        "field_action": form[field_name],
        "field": form[field_name[:-7]] if has_field else None
    }

    return field

