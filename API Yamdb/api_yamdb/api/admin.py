from django.contrib import admin

from reviews.models import Comment, Review, Category, Genre, Title, TitleGenre


class TitileInline(admin.TabularInline):
    model = TitleGenre
    extra = 1


class TitleAdmin(admin.ModelAdmin):
    inlines = (TitileInline, )


class GenreAdmin(admin.ModelAdmin):
    inlines = (TitileInline, )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'author',
                    'text',
                    'score',
                    'pub_date',
                    'title')
    list_filter = ('author', 'score', 'pub_date')
    search_fields = ('author', )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'author',
                    'text',
                    'pub_date',
                    'review')
    list_filter = ('author', 'pub_date')
    search_fields = ('author',)


admin.site.register(Category)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(TitleGenre)
