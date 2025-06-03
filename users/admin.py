from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import User

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type',
                 'profile_picture', 'bio', 'date_of_birth', 'phone_number', 'address',
                 'is_active', 'is_staff', 'date_joined')
        export_order = fields

@admin.register(User)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = UserResource
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture',
                                    'bio', 'date_of_birth', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser',
                                  'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
