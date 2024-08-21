from django.views.generic import TemplateView
from django.views.generic import DetailView
from .models import Post, Comment, Follow, Report, Profile
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
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get top-level comments (those without a parent)
        context['top_level_comments'] = self.object.comments.filter(parent__isnull=True)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_body = request.POST.get('comment_body')
        parent_id = request.POST.get('parent_id')

        if comment_body:
            parent_comment = None
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
            
            Comment.objects.create(
                post=self.object,
                author=request.user,
                body=comment_body,
                parent=parent_comment
            )
            return redirect('post_detail', slug=self.object.slug)
        
        context = self.get_context_data()
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the reason for the report...'})
        }

@login_required
def report_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            messages.success(request, 'The post has been reported and is being reviewed.')
            return redirect('post_detail', slug=slug)
    else:
        form = ReportForm()
    
    return render(request, 'report_form.html', {'form': form, 'post': post})

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

@login_required
def follow_toggle(request, pk):
    user_to_follow = get_object_or_404(User, pk=pk)
    follow_instance, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)

    if not created:
        follow_instance.delete()

    return redirect('account', pk=pk)

class AccountView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account.html'
    context_object_name = 'user_account'

    def get_object(self, queryset=None):
        user = User.objects.get(pk=self.kwargs['pk'])
        # Ensure the profile exists
        Profile.objects.get_or_create(user=user)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_own_account'] = self.request.user == self.get_object()
        
        context['posts'] = Post.objects.filter(author=self.get_object()).order_by('-created_on')
        
        if context['is_own_account']:
            context['email_form'] = forms.Form()  # Placeholder for the email form
            context['password_form'] = PasswordChangeForm(user=self.request.user)
            context['bio_form'] = BioForm(instance=self.get_object().profile)
        else:
            context['is_following'] = Follow.objects.filter(follower=self.request.user, following=self.get_object()).exists()

        context['follower_count'] = self.get_object().followers.count()
        context['following_count'] = self.get_object().following.count()

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

        elif 'bio_form' in request.POST:
            bio_form = BioForm(request.POST, instance=request.user.profile)
            if bio_form.is_valid():
                bio_form.save()
                messages.success(request, 'Your bio has been updated successfully!')
                return redirect('account', pk=user.pk)

        context = self.get_context_data()
        context['email_form'] = forms.Form()  # Placeholder for the email form
        context['password_form'] = PasswordChangeForm(user=request.user, data=request.POST)
        context['bio_form'] = BioForm(instance=request.user.profile)
        return render(request, self.template_name, context)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['content', 'image']
    template_name = 'edit_post.html'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.object.slug})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

class BioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...', 'maxlength': '300'})
        }
        labels = {
            'bio': 'Bio'
        }