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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import DetailView

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

class AccountView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account.html'
    context_object_name = 'user_account'

    def get_object(self, queryset=None):
        return User.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_own_account'] = self.request.user == self.get_object()
        
        if context['is_own_account']:
            context['email_form'] = forms.Form()  # Placeholder for the email form
            context['password_form'] = PasswordChangeForm(user=self.request.user)
        
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user != user:
            return redirect('home')  # Prevent users from updating others' accounts

        if 'email_form' in request.POST:
            email = request.POST.get('email')
            if email and not User.objects.filter(email=email).exists():
                user.email = email
                user.save()
                messages.success(request, 'Your email has been updated successfully!')
                return redirect('account', pk=user.pk)
            else:
                messages.error(request, 'This email is already in use or invalid.')
        
        elif 'password_form' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important to keep the user logged in after password change
                messages.success(request, 'Your password has been updated successfully!')
                return redirect('account', pk=user.pk)
            else:
                messages.error(request, 'Please correct the errors below.')
        
        context = self.get_context_data()
        context['email_form'] = forms.Form()  # Placeholder for the email form
        context['password_form'] = PasswordChangeForm(user=request.user, data=request.POST)
        return render(request, self.template_name, context)