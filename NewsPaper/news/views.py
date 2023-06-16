from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Category
from .forms import NewsForm
from .filters import NewsFilter
from .tasks import mail_new_post_to_subs


class NewsList(ListView):
    model = Post
    ordering = ["-creation_time"]
    template_name = "news_list.html"
    context_object_name = "news_list"
    paginate_by = 5


class NewsDetail(DetailView):
    model = Post
    template_name = "news_detail.html"
    context_object_name = "news_detail"


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'

    template_name = "news_add.html"
    form_class = NewsForm

    def form_valid(self, form):
        post = form.save()
        post.save()
        mail_new_post_to_subs.delay(post_pk=post.pk)
        return redirect('/news/')


class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'

    template_name = 'news_add.html'
    form_class = NewsForm
    success_url = '/news/'

    def get_object(self, **kwargs):
        _id = self.kwargs.get('pk')
        return Post.objects.get(pk=_id)


class NewsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'

    template_name = 'news_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


class NewsSearch(ListView):
    model = Post
    ordering = ['-creation_time']
    context_object_name = "news_list"
    template_name = 'news_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        return context


@login_required
def subscribe(request):
    user = request.user
    category = Category.objects.filter(name=request.GET["cat"])
    if category.exists():
        category[0].subscribers.add(user)

    return redirect('/news/')
