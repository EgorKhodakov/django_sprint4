from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Comment


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])

    def dispatch(self, request, *args, **kwargs):
        coment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        if coment.author != self.request.user:
            return redirect('blog:post_detail',
                            pk=self.kwargs['pk']
                            )
        return super().dispatch(request, *args, **kwargs)


class PostMixin():

    def filtered_post(self, list_post):
        return list_post.filter(
            pub_date__lte=datetime.today(),
            is_published=True,
            category__is_published=True
        )
