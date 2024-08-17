from django.contrib import admin
from django.urls import path, include
#from posts.views import my_posts

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('summernote/', include('django_summernote.urls')),
    path('', include('posts.urls'), name='posts'),
]
