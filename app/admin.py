from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SalesAdmin(admin.ModelAdmin):
    pass
# Register your models here.
