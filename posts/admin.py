from django.contrib import admin
from .models import Post
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('slug', 'status')
    search_fields = ['slug']
    list_filter = ('status',)
    summernote_fields = ('content',)