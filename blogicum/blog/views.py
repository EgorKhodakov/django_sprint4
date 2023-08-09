from datetime import datetime
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin


from blog.models import Post, Category, Comment, User
from .forms import CommentForm, PostForm, UserForm

PAGINATOR_FOR_PAGES = 10


class PostListView(ListView):
    paginate_by = PAGINATOR_FOR_PAGES
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=datetime.today(),
            is_published=True,
            category__is_published=True
            )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (
            not self.object.is_published
            and (self.object.author != request.user)

        ):
            raise Http404('Page was not found')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        context['comments'] = self.object.comments.select_related('author')
        context['form'] = CommentForm()
        return context


class PostCategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = PAGINATOR_FOR_PAGES

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
                                            Category,
                                            slug=self.kwargs['category_slug'],
                                            is_published=True
                                            )
        return context

    def get_queryset(self):
        current_time = datetime.now()
        return Post.objects.filter(
                                   category__slug=self.kwargs['category_slug'],
                                   category__is_published=True,
                                   pub_date__lte=current_time,
                                   is_published=True
                                   )


class PostCreateVIew(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


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
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class ProfileListView(ListView):
    paginate_by = PAGINATOR_FOR_PAGES
    template_name = 'blog/profile.html'
    model = Post

    def get_queryset(self):
        return self.model.objects.select_related('author').filter(
                                    author__username=self.kwargs['username']
                                    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User,
                                               username=self.kwargs['username']
                                               )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    def dispatch(self, request, *args, **kwargs):
        coment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        if coment.author != self.request.user:
            return redirect('blog:post_detail',
                            pk=self.kwargs['pk']
                            )
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm(instance=self.object)
        return context


class CommentDeleteView(CommentMixin, DeleteView):
    ...
