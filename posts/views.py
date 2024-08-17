from django.views.generic import TemplateView
from django.views.generic import DetailView
from .models import Post
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(status=1).order_by('-created_on')
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

class CreatePostView(FormView):
    form_class = PostForm
    template_name = 'index.html'
    success_url = '/'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)

@login_required(login_url='/accounts/login/')
def LikeView(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post_detail', args=[slug]))