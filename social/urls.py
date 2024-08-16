from django.contrib import admin
from django.urls import path
from posts.views import my_posts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', my_posts, name='posts'),
]
