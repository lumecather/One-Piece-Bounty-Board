from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, PirateProfile, PostBountyAuto


# --- Вспомогательный сериализатор для PostBountyAuto ---
class PostBountyAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostBountyAuto
        fields = ['enabled', 'percent', 'interval_days', 'last_run']


# 1. Базовый пользователь
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# 2. Профиль пирата (теперь role, organization, image)
class PirateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PirateProfile
        fields = ['user', 'image', 'role', 'organization']


# 3. Комментарий (добавлено поле image, автор только для чтения)
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'date', 'post', 'image']
        read_only_fields = ['post', 'author']   # автор назначается во view


# 4. Пост (добавлены bounty и вложенный bounty_auto)
class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    bounty_auto = PostBountyAutoSerializer(read_only=True)   # настройки авто‑поднятия

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'date', 'author', 'author_name',
            'image', 'bounty', 'bounty_auto', 'comments', 'comment_count'
        ]
        read_only_fields = ['author', 'date']