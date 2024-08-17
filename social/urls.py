from django.contrib import admin
from django.urls import path, include
#from posts.views import my_posts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls'), name='posts'),
]
