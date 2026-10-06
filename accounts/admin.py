from django.contrib import admin
from .models import CustomUser, AuthorProfile
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'bio', 'avatar', 'date_joined')
    list_filter = ("is_staff", "is_active","date_joined",)
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {"fields": ("bio", "avatar",)},
        ),)

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Дополнительная информация",
            {"fields": ("email", "bio", "avatar",)},
        ),)


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'portfolio_url')
    search_fields = ("user__username", "user__email", "specialization",)
