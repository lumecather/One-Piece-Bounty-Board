from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='basepage'),  # as_view() превращает класс в функцию
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
]
