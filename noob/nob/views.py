from .models import Post, Comment, PirateProfile
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin


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


class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = '/accounts/login/'
    model = Post
    form_class = PostForm
    template_name = 'nob/post_form.html'
    success_url = reverse_lazy('basepage')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


class ProfileView(LoginRequiredMixin, DetailView):
    login_url = '/accounts/login/'
    model = PirateProfile
    template_name = 'nob/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        if 'pk' in self.kwargs:
            return get_object_or_404(PirateProfile, pk=self.kwargs['pk'])
        return get_object_or_404(PirateProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.get_object().user == self.request.user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    login_url = '/accounts/login/'
    model = PirateProfile
    template_name = 'nob/profile_edit.html'
    fields = ['bounty', 'crew', 'devil_fruit', 'image', 'class1', 'status']
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(PirateProfile, user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})
