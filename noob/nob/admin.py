from django.contrib import admin

from .models import Post, Comment, PirateProfile


class PirateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', "image", 'role')
    list_filter = ('role',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', "organization", 'author', 'date', 'has_image')
    list_filter = ('author', 'date', "organization")
    search_fields = ('title', 'content')
    list_editable = ('title',)
    list_per_page = 10
    date_hierarchy = 'date'

    def has_image(self, obj):
        return bool(obj.image)

    has_image.short_description = 'Есть фото'
    has_image.boolean = True


admin.site.register(PirateProfile, PirateProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
