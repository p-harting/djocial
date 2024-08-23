from django.contrib import admin
from .models import Post, Comment, Follow, Report, Profile
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('content_snippet', 'status', 'slug')
    search_fields = ['slug']
    list_filter = ('status',)
    summernote_fields = ('content',)

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(
            obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content Snippet'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('body_snippet', 'post', 'author', 'approved', 'created_on')
    search_fields = ['body', 'author__username', 'post__slug']
    list_filter = ('approved', 'created_on', 'post')
    ordering = ('created_on',)

    def body_snippet(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_snippet.short_description = 'Comment Snippet'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_on')
    search_fields = ['follower__username', 'following__username']
    list_filter = ('created_on',)
    ordering = ('created_on',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'created_on', 'reviewed')
    search_fields = ['post__slug', 'reporter__username']
    list_filter = ('reviewed', 'created_on')
    ordering = ('-created_on',)
    actions = ['mark_as_reviewed']

    def mark_as_reviewed(self, request, queryset):
        queryset.update(reviewed=True)
    mark_as_reviewed.short_description = "Mark as reviewed"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ['user__username', 'bio']
    list_filter = ('user',)
