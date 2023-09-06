from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    ordering = ('username', )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollownAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following']
    search_fields = [
        'following__username',
        'following__email',
        'follower__username',
        'follower__email'
    ]
    list_filter = ['following__username', 'follower__username']
    empty_value_display = '-пусто-'
