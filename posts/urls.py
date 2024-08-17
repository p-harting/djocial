from . import views
from django.urls import path
from .views import HomeView, PostDetailView, CreatePostView, LikeView, AccountView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', CreatePostView.as_view(), name='create_post'),
    path('like/<slug:slug>/', LikeView, name='like_post'),
    path('account/<int:pk>', AccountView.as_view(), name='account'),
]
