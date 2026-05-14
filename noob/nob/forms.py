from django import forms
from .models import Post
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', "image"]
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваш комментарий'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', "bounty"]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
