from .models import Post, Comment
from django.views.generic import ListView, DetailView, CreateView
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.shortcuts import redirect


class PostListView(ListView):
    model = Post
    template_name = 'nob/basepage.html'
    context_object_name = 'posts'
    ordering = ['-date']  # новые сначала


class PostDetailView(DetailView):
    model = Post
    template_name = 'nob/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('-date')
        context['comment_form'] = CommentForm()  # добавляем форму в контекст
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.save()
            return redirect('post_detail', pk=self.object.pk)
        else:
            context = self.get_context_data()
            context['comment_form'] = form
            return self.render_to_response(context)


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'nob/post_form.html'
    success_url = reverse_lazy('basepage')
