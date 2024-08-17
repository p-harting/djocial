from . import views
from django.urls import path
from .views import HomeView, PostDetailView, CreatePostView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', CreatePostView.as_view(), name='create_post'),
]
