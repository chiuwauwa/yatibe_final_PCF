from django.forms import models
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Group, Comment


class PostForm(models.ModelForm):
    text = forms.CharField(
        label=_("Текст"),
        strip=True,
        required=True,
        widget=forms.Textarea,
    )
    group = forms.ModelChoiceField(
        label=_("Группа"),
        required=False,
        queryset=Group.objects.all(),
    )

    class Meta:
        model = Post
        fields = ("text", "group", "image")


class CommentForm(models.ModelForm):
    text = forms.CharField(
        label=_("Текст"),
        strip=True,
        required=True,
        widget=forms.Textarea,
    )

    class Meta:
        model = Comment
        fields = ("text",)
