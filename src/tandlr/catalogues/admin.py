from django.contrib import admin

from .models import University


@admin.register(University)
class AdminUniversity(admin.ModelAdmin):
    list_display = ('name',)
