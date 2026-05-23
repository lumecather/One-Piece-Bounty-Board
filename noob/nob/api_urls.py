from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()

router.register(r'posts', views.PostViewSet)  # /api/posts/
router.register(r'comments', views.CommentViewSet)  # /api/comments/
router.register(r'profiles', views.PirateProfileViewSet)  # /api/profiles/

urlpatterns = [
    path('', include(router.urls)),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]