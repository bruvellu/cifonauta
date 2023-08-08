from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserCifonautaCreationForm
from .models import UserCifonauta

@admin.action(description="Tornar autor")
def make_author_action(modeladmin, request, queryset):
    for pessoa in queryset:
        pessoa.is_author = True
        pessoa.save()

@admin.action(description="Remover autor")
def remove_author_action(modeladmin, request, queryset):
    for pessoa in queryset:
        pessoa.is_author = False
        pessoa.save()

class UserCifonautaAdmin(UserAdmin):
    add_form = UserCifonautaCreationForm
    model = UserCifonauta
    list_display = ("username", "email", "is_author", "is_staff", "is_active", 'orcid', "first_name", "last_name", "idlattes")
    list_filter = ("email", "is_author", "is_staff", "is_active", "username", 'orcid', "first_name", "last_name", "idlattes")
    fieldsets = (
        (None, {"fields": ("email", "password", "username", 'orcid', "first_name", "last_name", "idlattes")}),
        ("Permissions", {"fields": ("is_author", "is_staff", "is_active", "specialist_of", "curator_of")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff", 
                "is_active", "username", 'orcid', "first_name", "last_name", "idlattes"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    actions = [make_author_action, remove_author_action]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.is_author:
            print(fieldsets)
            fieldsets[1][1]['fields'] = ("is_author", "is_staff", "is_active", "specialist_of", "curator_of")
        else:
            fieldsets[1][1]['fields'] = ("is_author", "is_staff", "is_active")
        return fieldsets


admin.site.register(UserCifonauta, UserCifonautaAdmin)