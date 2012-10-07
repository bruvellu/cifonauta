#######################################
# TransMeta modified version
#
# Integration to DataTrans (so TransMeta works only as cacher)
#
#######################################
import copy

from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.utils.translation import get_language
from django.utils.functional import lazy

from datatrans.utils import REGISTRY, _pre_save, _post_save, get_current_language, KeyValue, get_default_language
from datatrans.models import KeyValue

LANGUAGE_CODE = 0
LANGUAGE_NAME = 1


def get_languages():
    return getattr(settings, 'TRANSMETA_LANGUAGES', settings.LANGUAGES)


def get_real_fieldname(field, lang=None):
    if lang is None:
        lang = get_language()
    lang = lang.split('-')[0] # both 'en-US' and 'en' -> 'en'
    return str('%s_%s' % (field, lang))


def get_field_language(real_field):
    """ return language for a field. i.e. returns "en" for "name_en" """
    return real_field.split('_')[1]


def get_fallback_fieldname(field, lang=None):
    return get_real_fieldname(field, lang=fallback_language())


def get_real_fieldname_in_each_language(field):
    return [get_real_fieldname(field, lang[LANGUAGE_CODE])
            for lang in get_languages()]


def canonical_fieldname(db_field):
    """ all "description_en", "description_fr", etc. field names will return "description" """
    return getattr(db_field, 'original_fieldname', db_field.name) # original_fieldname is set by transmeta


def fallback_language():
    """ returns fallback language """
    return getattr(settings, 'TRANSMETA_DEFAULT_LANGUAGE', \
                   settings.LANGUAGE_CODE)


def get_all_translatable_fields(model, model_trans_fields=None, column_in_current_table=False):
    """ returns all translatable fields in a model (including superclasses ones) """
    if model_trans_fields is None:
        model_trans_fields = set()
    model_trans_fields.update(set(getattr(model._meta, 'translatable_fields', [])))
    for parent in model.__bases__:
        if getattr(parent, '_meta', None) and (not column_in_current_table or parent._meta.abstract):
            get_all_translatable_fields(parent, model_trans_fields, column_in_current_table)
    return tuple(model_trans_fields)


def default_value(field):
    '''
    When accessing to the name of the field itself, the value
    in the current language will be returned. Unless it's set,
    the value in the default language will be returned.
    '''

    def default_value_func(self):
        attname = lambda x: get_real_fieldname(field, x)

        if getattr(self, attname(get_language()), None):
            result = getattr(self, attname(get_language()))
        elif getattr(self, attname(get_language()[:2]), None):
            result = getattr(self, attname(get_language()[:2]))
        else:
            default_language = fallback_language()
            result = getattr(self, attname(default_language), None)
        return result

    return default_value_func


class TransMeta(models.base.ModelBase):
    '''
    Metaclass that allow a django field, to store a value for
    every language. The syntax to us it is next:

        class MyClass(models.Model):
            __metaclass__ = transmeta.TransMeta

            my_field = models.CharField(max_length=20)
            my_i18n_field = models.CharField(max_length=30)

            class Meta:
                translate = ('my_i18n_field',)

    Then we'll be able to access a specific language by
    <field_name>_<language_code>. If just <field_name> is
    accessed, we'll get the value of the current language,
    or if null, the value in the default language.
    '''

    def __new__(cls, name, bases, attrs):
        attrs = SortedDict(attrs)
        if 'Meta' in attrs and hasattr(attrs['Meta'], 'translate'):
            fields = attrs['Meta'].translate
            delattr(attrs['Meta'], 'translate')
        else:
            new_class = super(TransMeta, cls).__new__(cls, name, bases, attrs)
            # we inherits possible translatable_fields from superclasses
            abstract_model_bases = [base for base in bases if hasattr(base, '_meta') \
                                    and base._meta.abstract]
            translatable_fields = []
            for base in abstract_model_bases:
                if hasattr(base._meta, 'translatable_fields'):
                    translatable_fields.extend(list(base._meta.translatable_fields))
            new_class._meta.translatable_fields = tuple(translatable_fields)
            return new_class

        if not isinstance(fields, tuple):
            raise ImproperlyConfigured("Meta's translate attribute must be a tuple")

        default_language = fallback_language()

        for field in fields:
            if not field in attrs or \
               not isinstance(attrs[field], models.fields.Field):
                    raise ImproperlyConfigured(
                        "There is no field %(field)s in model %(name)s, "\
                        "as specified in Meta's translate attribute" % \
                        dict(field=field, name=name))
            original_attr = attrs[field]
            
            for lang in get_languages():
                lang_code = lang[LANGUAGE_CODE]
                lang_code = lang[LANGUAGE_CODE]
                lang_attr = copy.copy(original_attr)
                lang_attr.original_fieldname = field
                lang_attr_name = get_real_fieldname(field, lang_code)
                if lang_code != default_language:
                    # only will be required for default language
                    if not lang_attr.null and lang_attr.default is NOT_PROVIDED:
                        lang_attr.null = True
                    if not lang_attr.blank:
                        lang_attr.blank = True
                if hasattr(lang_attr, 'verbose_name'):
                    lang_attr.verbose_name = LazyString(lang_attr.verbose_name, lang_code)
                attrs[lang_attr_name] = lang_attr
            #attrs[field].name = FieldDescriptor(attrs[field].name)
#            del attrs[field]
            #attrs[field] = property(default_value(field))

        new_class = super(TransMeta, cls).__new__(cls, name, bases, attrs)
#        if 'Meta' in attrs and hasattr(attrs['Meta'], 'abstract'):
#            pass
#        else:
#            print new_class, attrs
#            register(new_class, fields )
        if hasattr(new_class, '_meta'):
            new_class._meta.translatable_fields = fields
#        if hasattr(new_class, 'title'):
#            new_class.title = attrs['title_en']
        return new_class

def prepare_value(self, str='true'):
    return 'DEFAULT'


from django.db.models import Field
class FieldDescriptor(object):
    def __init__(self, name):
        self.name = name
    def __get__(self, instance, owner):
        return  default_value( self.instance )
        


class LazyString(object):

    def __init__(self, proxy, lang):
        self.proxy = proxy
        self.lang = lang

    def __unicode__(self):
        return u'%s %s' % (self.proxy, self.lang)



#### Adding support to work with DataTrans


#def _post_mark(sender, instance, created, **kwargs):
#    print sender, instance, created
#
#models.signals.post_save.connect(_post_mark, sender=KeyValue)     

class FieldModified(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return 'NOP'
        lang_code = get_current_language()
        key = instance.__dict__[self.name]
        if not key:
            return u''
        return KeyValue.objects.lookup(key, lang_code)
#
#    def __set__(self, instance, value):
#        lang_code = get_current_language()
#        default_lang = get_default_language()
#
#        if lang_code == default_lang or not self.name in instance.__dict__:
#            instance.__dict__[self.name] = value
#        else:
#            original = instance.__dict__[self.name]
#            if original == u'':
#                instance.__dict__[self.name] = value
#                original = value
#
#            kv = KeyValue.objects.get_keyvalue(original, lang_code)
#            kv.value = value
#            kv.edited = True
#            kv.save()
#
#        return None



def _post_init(sender, instance, **kwargs):
    fields = REGISTRY[sender]
    for field in fields.values():
        lang_code = get_current_language()
        fname = get_real_fieldname(field.name, lang_code)
        if getattr(instance, fname):
            setattr(instance, field.name, getattr(instance, fname))
#            if str(sender) == "<class 'meta.models.Image'>":
#                print get_language(), field.name, getattr(instance, field.name), lang_code

def register(model, fields):
    '''
    fields = ('field1', 'field2', ...)

    For example:

    register(Image, ('caption', 'description')

    '''

    if not model in REGISTRY:
        # create a fields dict (models apparently lack this?!)
        fields = dict([(f.name, f) for f in model._meta._fields() if f.name in fields])

        REGISTRY[model] = fields
        
        models.signals.pre_save.connect(_pre_save, sender=model)
        models.signals.post_save.connect(_post_save, sender=model)
        models.signals.post_init.connect(_post_init, sender=model)  
        
#        for field in fields.values():
#            setattr(model, field.name, FieldModified(field.name))
                      