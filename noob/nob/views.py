from .models import Post, Comment, PirateProfile, PostBountyAuto
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .forms import PostForm, CommentForm, PostEditForm
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

        # Проверка: своя организация
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
        return super().form_valid(form)


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
        context['can_edit'] = self.get_object().user == self.request.user

        profile = self.get_object()

        if profile.organization:
            users_in_org = PirateProfile.objects.filter(
                organization=profile.organization
            ).values_list('user', flat=True)

            org_posts = Post.objects.filter(
                author_id__in=users_in_org
            ).order_by('-date')

            context['org_posts'] = org_posts
            context['organization_name'] = profile.organization
        else:
            context['org_posts'] = []
            context['organization_name'] = None

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    login_url = '/accounts/login/'
    model = PirateProfile
    template_name = 'nob/profile_edit.html'
    fields = ['image']
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(PirateProfile, user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})


class PostViewSet(viewsets.ModelViewSet):
    """
    API для работы с постами (розыскными объявлениями)
    """
    queryset = Post.objects.all().select_related('author').prefetch_related('comments')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author__username', 'date']  # фильтр по автору и дате
    search_fields = ['title', 'content']  # поиск по заголовку и тексту
    ordering_fields = ['date', 'title']  # сортировка
    ordering = ['-date']  # по умолчанию: новые сверху

    def get_permissions(self):
        """
        Назначаем права доступа в зависимости от действия
        """
        if self.action == 'create':
            # Создать пост может только авторизованный
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Изменить/удалить может только автор
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        # Список и детальная страница — всем
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """
        При создании поста автоматически подставляем автора
        """
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API для комментариев
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'author']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """
        При создании комментария можно указать пост из данных
        """
        serializer.save()


class PirateProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для профилей пиратов (только чтение)
    """
    queryset = PirateProfile.objects.all().select_related('user')
    serializer_class = PirateProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['crew', 'devil_fruit']
    search_fields = ['user__username', 'crew']

    def get_permissions(self):
        return [permissions.AllowAny()]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PirateProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Post)
def create_bounty_auto(sender, instance, created, **kwargs):
    if created:
        PostBountyAuto.objects.create(post=instance)
