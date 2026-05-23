from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, PirateProfile, PostBountyAuto


class PostBountyAutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostBountyAuto
        fields = ['enabled', 'percent', 'interval_days', 'last_run']


# 1. Базовый пользователь
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PirateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PirateProfile
        fields = ['user', 'image', 'role', 'organization']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'date', 'post', 'image']
        read_only_fields = ['post', 'author']


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    bounty_auto = PostBountyAutoSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'date', 'author', 'author_name',
            'image', 'bounty', 'bounty_auto', 'comments', 'comment_count'
        ]
        read_only_fields = ['author', 'date']