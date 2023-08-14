from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)

from blog.models import Category, Comment, Post, User
from .forms import CommentForm, PostForm, UserForm
from .utils import CommentMixin, PostMixin

PAGINATOR_POST_LIST = 10
PAGINATOR_POST_CATEGORY = 10
PAGINATOR_PROFILE_LIST = 10


class PostListView(PostMixin, ListView):
    paginate_by = PAGINATOR_POST_LIST
    template_name = 'blog/index.html'

    def get_queryset(self):
        return self.filtered_post(Post.objects.all())


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        if (
            not self.get_object().is_published
            and (self.get_object().author != request.user)

        ):
            raise Http404('Page was not found')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            comments=self.object.comments.select_related('author'),
            form=CommentForm()
        )


class PostCategoryView(PostMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATOR_POST_CATEGORY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context

    def get_queryset(self):
        category = Category.objects.get(slug=self.kwargs['category_slug'])
        return self.filtered_post(category.posts.all())


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user]
        )


class PostMixin(LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author != self.request.user:
            return redirect('blog:post_detail',
                            pk=self.kwargs['pk']
                            )
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class PostDeleteView(PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=PostForm(instance=self.obects)
        )

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user])


class ProfileListView(ListView):
    paginate_by = PAGINATOR_PROFILE_LIST
    template_name = 'blog/profile.html'
    model = Post

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        return self.get_object().post.all()

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            profile=get_object_or_404(User, username=self.kwargs['username'])
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        return dict(super().get_context_data(**kwargs), form=CommentForm())

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        return dict(
            super().get_context_data(**kwargs),
            form=CommentForm(instance=self.object)
        )


class CommentDeleteView(CommentMixin, DeleteView):
    ...
