from django import forms
from .models import Post, PostBountyAuto, PirateProfile
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', "image"]
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your comment'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', "bounty"]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


class PostEditForm(forms.ModelForm):
    auto_enabled = forms.BooleanField(required=False, label="auto raise bounty")
    auto_percent = forms.IntegerField(min_value=1, max_value=500, label="raise percentage", initial=5)
    auto_interval = forms.IntegerField(min_value=1, max_value=365, label="interval (days)", initial=7)

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'bounty']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                auto = self.instance.bounty_auto
                self.initial['auto_enabled'] = auto.enabled
                self.initial['auto_percent'] = auto.percent
                self.initial['auto_interval'] = auto.interval_days
            except PostBountyAuto.DoesNotExist:
                pass

    def save(self, commit=True):
        post = super().save(commit=commit)
        if commit:
            auto, _ = PostBountyAuto.objects.get_or_create(post=post)
            auto.enabled = self.cleaned_data['auto_enabled']
            auto.percent = self.cleaned_data['auto_percent']
            auto.interval_days = self.cleaned_data['auto_interval']
            auto.save()
        return post


class ProfileEditForm(forms.ModelForm):
    role_choice = forms.ChoiceField(
        choices=[('just_user', 'user'), ('hunter', 'bounty hunter'), ("pirate", "pirate")],
        required=False,
        label='Роль'
    )

    class Meta:
        model = PirateProfile
        fields = ['image', 'role_choice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.role in ['admin', 'official']:
            self.fields['role_choice'].widget.attrs['disabled'] = True
            self.fields['role_choice'].help_text = 'Cant change this role'
        else:
            self.fields['role_choice'].initial = self.instance.role if self.instance.role in ['just_user', 'hunter',
                                                                                              "pirate"] else 'just_user'
