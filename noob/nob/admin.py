from django.contrib import admin

from .models import Post, Comment, PirateProfile


class PirateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bounty', 'crew', 'devil_fruit', "class1", "status")


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'date', 'has_image')
    list_filter = ('author', 'date')
    search_fields = ('title', 'content')
    list_editable = ('title',)  # можно редактировать прямо в списке
    list_per_page = 10  # пагинация в админке
    date_hierarchy = 'date'  # навигация по датам

    def has_image(self, obj):
        return bool(obj.image)

    has_image.short_description = 'Есть фото'
    has_image.boolean = True


admin.site.register(PirateProfile, PirateProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
