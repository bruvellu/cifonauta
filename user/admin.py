from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserCifonautaCreationForm
from .models import UserCifonauta

class UserCifonautaAdmin(UserAdmin):
    add_form = UserCifonautaCreationForm
    model = UserCifonauta
    list_display = ("email", "is_staff", "is_active", "username", 'orcid', "first_name", "last_name", "idlattes")
    list_filter = ("email", "curadoria", "is_staff", "is_active", "username", 'orcid', "first_name", "last_name", "idlattes")
    fieldsets = (
        (None, {"fields": ("email", "password", "username", 'orcid', "first_name", "last_name", "idlattes")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "curadoria","groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions", "username", 'orcid', "first_name", "last_name", "idlattes"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(UserCifonauta, UserCifonautaAdmin)

