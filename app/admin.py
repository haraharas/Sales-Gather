from django.contrib import admin
from .models import Sale
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _


@admin.register(Sale)
class SalesAdmin(admin.ModelAdmin):
    pass
# Register your models here.
