from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, PirateProfile


# 1. Сериализатор для пользователя (базовый)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# 2. Сериализатор для профиля пирата
class PirateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PirateProfile
        fields = ['user', 'bounty', 'crew', 'devil_fruit', 'image']


# 3. Сериализатор для комментариев
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'date', 'post']
        read_only_fields = ['post']


# 4. Сериализатор для постов (основной)
class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'date', 'author', 'author_name',
                  'image', 'comments', 'comment_count']
        read_only_fields = ['author', 'date']