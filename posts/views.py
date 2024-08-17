from django.views.generic import TemplateView
from .models import Post

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(status=1).order_by('-created_on')
        return context