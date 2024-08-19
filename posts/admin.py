from django.contrib import admin
from .models import Post, Comment, Follow
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('slug', 'status')
    search_fields = ['slug']
    list_filter = ('status',)
    summernote_fields = ('content',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'body', 'approved', 'created_on')
    search_fields = ['body', 'author__username', 'post__slug']
    list_filter = ('approved', 'created_on', 'post')
    ordering = ('created_on',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_on')
    search_fields = ['follower__username', 'following__username']
    list_filter = ('created_on',)
    ordering = ('created_on',)