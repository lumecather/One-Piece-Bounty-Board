from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# Создаём роутер
router = DefaultRouter()

# Регистрируем наши ViewSet'ы
router.register(r'posts', views.PostViewSet)  # /api/posts/
router.register(r'comments', views.CommentViewSet)  # /api/comments/
router.register(r'profiles', views.PirateProfileViewSet)  # /api/profiles/

urlpatterns = [
    # Все URL от роутера
    path('', include(router.urls)),

    # JWT токены
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]