from django.contrib import admin
from blog.models import Post, Tag, Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'short_text', 'published_at')
    list_select_related = ('author', 'post')
    raw_id_fields = ('post', 'author')
    search_fields = ('text', 'author__username')

    def short_text(self, obj):
        return obj.text[:50] if obj.text else ''

    short_text.short_description = 'Text snippet'


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'comments_count')
    list_select_related = ('author',)
    raw_id_fields = ('author', 'tags', 'likes')
    filter_horizontal = ('tags',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _comments_count=Count('comments')
        )

    def comments_count(self, obj):
        return obj._comments_count

    comments_count.admin_order_field = '_comments_count'


class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'posts_count')
    search_fields = ('title',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _posts_count=Count('posts')
        )

    def posts_count(self, obj):
        return obj._posts_count

    posts_count.admin_order_field = '_posts_count'


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)
