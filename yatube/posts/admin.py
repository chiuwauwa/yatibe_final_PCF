from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)


class GroupAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'title',
        'slug',
        'description',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
