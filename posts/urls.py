from . import views
from django.urls import path
from .views import HomeView, PostDetailView, CreatePostView, LikeView, AccountView, follow_toggle, report_post

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', CreatePostView.as_view(), name='create_post'),
    path('like/<slug:slug>/', LikeView, name='like_post'),
    path('account/<int:pk>', AccountView.as_view(), name='account'),
    path('follow_toggle/<int:pk>/', follow_toggle, name='follow_toggle'),
    path('report/<slug:slug>/', report_post, name='report_post'),
]
