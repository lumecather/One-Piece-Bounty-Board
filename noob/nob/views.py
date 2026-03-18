from .models import Post, Comment, PirateProfile
from django.views.generic import ListView, DetailView, CreateView
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.signals import post_save
from django.dispatch import receiver


class PostListView(ListView):
    model = Post
    template_name = 'nob/basepage.html'
    context_object_name = 'posts'
    ordering = ['-date']  # новые сначала


class PostDetailView(LoginRequiredMixin, DetailView):
    login_url = '/accounts/login/'
    model = Post
    template_name = 'nob/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('-date')
        context['comment_form'] = CommentForm()  # добавляем форму в контекст
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
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


class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


@receiver(post_save, sender=User)
def create_pirate_profile(sender, instance, created, **kwargs):
    if created:
        PirateProfile.objects.create(user=instance)
