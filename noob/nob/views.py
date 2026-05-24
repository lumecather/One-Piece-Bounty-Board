from .models import Post, Comment, PirateProfile, PostBountyAuto
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import PostForm, CommentForm, PostEditForm, ProfileEditForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .serializers import PostSerializer, CommentSerializer, PirateProfileSerializer
from .permissions import IsAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from .tasks import send_welcome_email
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages


class PostListView(ListView):
    model = Post
    template_name = 'nob/basepage.html'
    context_object_name = 'posts'
    ordering = ['-date']  # новые сначала


class PostDetailView(DetailView):
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
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=self.object.pk)
        else:
            context = self.get_context_data()
            context['comment_form'] = form
            return self.render_to_response(context)


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'nob/post_edit.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        user_org = request.user.profile.organization if hasattr(request.user, 'profile') else None
        post_org = post.author.profile.organization if hasattr(post.author, 'profile') else None

        if not user_org or not post_org or user_org != post_org:
            messages.error(request, 'Вы можете редактировать только посты своей организации')
            return redirect('post_detail', pk=post.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Пост обновлен!')
        return super().form_valid(form)


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    login_url = '/accounts/login/'
    model = Post
    form_class = PostForm
    template_name = 'nob/post_form.html'
    success_url = reverse_lazy('basepage')

    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role in ['official', 'admin']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.organization = self.request.user.profile.organization
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('basepage')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.success_url)


class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Отправляем письмо в фоне (не ждём)
        send_welcome_email.delay(self.object.email, self.object.username)
        return response


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
        profile = self.get_object()

        context['can_edit'] = profile.user == self.request.user

        if profile.organization:
            org_posts = Post.objects.filter(
                organization=profile.organization
            ).order_by('-date')

            context['org_posts'] = org_posts
            context['organization_name'] = profile.organization
        else:
            context['org_posts'] = Post.objects.none()
            context['organization_name'] = None

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = PirateProfile
    form_class = ProfileEditForm
    template_name = 'nob/profile_edit.html'
    context_object_name = 'profile'
    login_url = '/accounts/login/'
    success_url = reverse_lazy('profile_self')

    def get_object(self):
        return get_object_or_404(PirateProfile, user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        profile = form.save(commit=False)
        role_choice = form.cleaned_data.get('role_choice')
        if role_choice and profile.role not in ['admin', 'official']:
            profile.role = role_choice
            if profile.role != 'official':
                profile.organization = ''
        profile.save()
        return super().form_valid(form)


class PostViewSet(viewsets.ModelViewSet):
    """
    API для постов (розыскных объявлений).
    """
    queryset = Post.objects.all().select_related('author').prefetch_related('comments', 'bounty_auto')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author__username', 'date']
    search_fields = ['title', 'content']
    ordering_fields = ['date', 'title', 'bounty']  # добавил сортировку по награде
    ordering = ['-date']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API для комментариев.
    """
    queryset = Comment.objects.all().select_related('author', 'post')
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'author']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Автор всегда текущий пользователь, пост можно передать в данных
        serializer.save(author=self.request.user)


class PirateProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для профилей (только чтение).
    """
    queryset = PirateProfile.objects.all().select_related('user')
    serializer_class = PirateProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'organization']  # актуальные поля
    search_fields = ['user__username', 'organization']  # поиск по нику или организации

    def get_permissions(self):
        return [permissions.AllowAny()]


@receiver(post_save, sender=Post)
def create_bounty_auto(sender, instance, created, **kwargs):
    if created:
        PostBountyAuto.objects.create(post=instance)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else PirateProfile.Role.USERR
        organization = 'admins' if instance.is_superuser else ''
        PirateProfile.objects.create(
            user=instance,
            role=role,
            organization=organization
        )
    else:
        PirateProfile.objects.get_or_create(user=instance)