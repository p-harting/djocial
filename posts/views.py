from django.views.generic import TemplateView, DetailView, FormView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count
from django import forms
from datetime import timedelta
from .models import Post, Comment, Follow, Report, Profile


class HomeView(TemplateView):
    # Homepage view, accessible to all users
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feed_type = self.request.GET.get('feed', 'trending')
        page_number = self.request.GET.get('page', 1)

        # Filter posts based on feed type
        if feed_type == 'followers' and self.request.user.is_authenticated:
            following_users = Follow.objects.filter(
                            follower=self.request.user
            ).values_list('following', flat=True)
            posts = Post.objects.filter(
                    author__in=following_users, status=1
            ).order_by('-created_on')
        else:
            seven_days_ago = timezone.now() - timedelta(days=7)
            posts = Post.objects.filter(
                    status=1, created_on__gte=seven_days_ago
            ).annotate(num_likes=Count('likes')).order_by('-num_likes',
                                                          '-created_on')

        paginator = Paginator(posts, 7)
        page_obj = paginator.get_page(page_number)

        context['posts'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['feed_type'] = feed_type
        return context

    def get(self, request, *args, **kwargs):
        # Handle AJAX requests for infinite scrolling
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            page_number = request.GET.get('page', 1)
            feed_type = request.GET.get('feed', 'trending')

            if feed_type == 'followers' and request.user.is_authenticated:
                following_users = Follow.objects.filter(
                    follower=request.user
                    ).values_list('following', flat=True)
                posts = Post.objects.filter(
                    author__in=following_users, status=1
                    ).order_by('-created_on')
            else:
                seven_days_ago = timezone.now() - timedelta(days=7)
                posts = Post.objects.filter(
                    status=1, created_on__gte=seven_days_ago
                    ).annotate(num_likes=Count('likes')).order_by(
                        '-num_likes', '-created_on')

            paginator = Paginator(posts, 7)
            page_obj = paginator.get_page(page_number)
            html = render_to_string(
                'partials/post_list.html', {'posts': page_obj})
            has_next = page_obj.has_next()
            return JsonResponse({'html': html, 'has_next': has_next})

        return super().get(request, *args, **kwargs)


class PostDetailView(LoginRequiredMixin, DetailView):
    # View for individual post details
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_level_comments'] = self.object.comments.filter(
            parent__isnull=True)
        return context

    def post(self, request, *args, **kwargs):
        # Handle comment submission
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


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'placeholder': "What's new...",
                'maxlength': 350
            }
        ),
        max_length=350,  # Enforces 350 characters limit
        required=True,
        label=''
    )
    image = forms.ImageField(required=False, label='Image')

    class Meta:
        model = Post
        fields = ['content', 'image']


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Describe the reason for the report...'
                }
            )
        }


@login_required(login_url='/accounts/login/')
def report_post(request, slug):
    # View for reporting a post
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            messages.success(
                request, 'The post has been reported and is being reviewed.')
            return redirect('post_detail', slug=slug)
    else:
        form = ReportForm()
    return render(request, 'report_form.html', {'form': form, 'post': post})


class CreatePostView(LoginRequiredMixin, FormView):
    form_class = PostForm
    template_name = 'index.html'
    success_url = '/'
    login_url = '/accounts/login/'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)


@login_required(login_url='/accounts/login/')
def LikeView(request, slug):
    # View for liking/unliking a post
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post_detail', args=[slug]))


@login_required(login_url='/accounts/login/')
def follow_toggle(request, pk):
    # View for following/unfollowing a user
    user_to_follow = get_object_or_404(User, pk=pk)
    follow_instance, created = Follow.objects.get_or_create(
        follower=request.user, following=user_to_follow)

    if not created:
        follow_instance.delete()

    return redirect('account', pk=pk)


class AccountView(LoginRequiredMixin, DetailView):
    # View for user account details
    model = User
    template_name = 'account.html'
    context_object_name = 'user_account'
    login_url = '/accounts/login/'

    def get_object(self, queryset=None):
        user = User.objects.get(pk=self.kwargs['pk'])
        Profile.objects.get_or_create(user=user)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_own_account'] = self.request.user == self.get_object()
        context['posts'] = Post.objects.filter(
            author=self.get_object()).order_by('-created_on')
        if context['is_own_account']:
            context['email_form'] = forms.Form()
            context['password_form'] = PasswordChangeForm(
                user=self.request.user)
            context['bio_form'] = BioForm(instance=self.get_object().profile)
        else:
            context['is_following'] = Follow.objects.filter(
                follower=self.request.user, following=self.get_object()
                ).exists()

        context['follower_count'] = self.get_object().followers.count()
        context['following_count'] = self.get_object().following.count()

        return context

    def post(self, request, *args, **kwargs):
        # Handle account updates
        user = self.get_object()
        if request.user != user:
            return redirect('home')

        if 'email_form' in request.POST:
            email = request.POST.get('email')
            if email and not User.objects.filter(email=email).exists():
                user.email = email
                user.save()
                messages.success(
                    request, 'Your email has been updated successfully!')
                return redirect('account', pk=user.pk)
            else:
                messages.error(
                    request, 'This email is already in use or invalid.')
        elif 'password_form' in request.POST:
            password_form = PasswordChangeForm(
                user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request, 'Your password has been updated successfully!')
                return redirect('account', pk=user.pk)
            else:
                messages.error(request, 'Please correct the errors below.')

        elif 'bio_form' in request.POST:
            bio_form = BioForm(request.POST, instance=request.user.profile)
            if bio_form.is_valid():
                bio_form.save()
                messages.success(
                    request, 'Your bio has been updated successfully!')
                return redirect('account', pk=user.pk)

        context = self.get_context_data()
        context['email_form'] = forms.Form()
        context['password_form'] = PasswordChangeForm(
            user=request.user, data=request.POST)
        context['bio_form'] = BioForm(instance=request.user.profile)
        return render(request, self.template_name, context)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['content', 'image']
    template_name = 'edit_post.html'
    login_url = '/accounts/login/'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.object.slug})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    # View for deleting a post
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')
    login_url = '/accounts/login/'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


class BioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Tell us about yourself...',
                    'maxlength': '300'
                    }
                )
        }
        labels = {
            'bio': 'Bio'
        }


@login_required(login_url='/accounts/login/')
def search_results(request):
    # View for search results
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(username__icontains=query)
        posts = Post.objects.filter(content__icontains=query)
    else:
        users = User.objects.none()
        posts = Post.objects.none()

    context = {
        'query': query,
        'users': users,
        'posts': posts,
    }
    return render(request, 'search_results.html', context)
