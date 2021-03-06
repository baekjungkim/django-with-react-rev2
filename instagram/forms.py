from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "photo",
            "caption",
            "location",
        ]

        # Model이 CharField 일경우 TextArea로 변경할수 있다.
        # widgets = {"caption": forms.Textarea,}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "message",
        ]
