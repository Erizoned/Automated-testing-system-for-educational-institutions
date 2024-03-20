from django.contrib import admin
from .models import *
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'user_type', 'is_staff', 'is_active']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('user_type', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'user_type')}
        ),
    )
    search_fields = ['username']
    ordering = ['username']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Subject)
admin.site.register(CustomGroup)
admin.site.register(Test)
admin.site.register(QuesModel)
admin.site.register(UserResult)
admin.site.register(StudentAnswer)
