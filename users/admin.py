from django.contrib import admin
from django.forms.models import model_to_dict

from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "role")
    list_filter = ("role",)
    search_fields = ("email", "username")