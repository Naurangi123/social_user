from django import forms

from .models import Post, Comment, MessageModel


# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True


class PostForm(forms.ModelForm):
    body = forms.CharField(label="", widget=forms.Textarea(attrs={'rows': '2', 'placeholder': 'Post Something...'}))

    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['body', 'image']


class CommentForm(forms.ModelForm):
    comment = forms.CharField(label="", widget=forms.Textarea(attrs={'rows': '1', 'placeholder': 'add a comment'}))

    class Meta:
        model = Comment

        fields = ['comment']


class ThreadForm(forms.Form):
    username = forms.CharField(label="", max_length=300)


class MessageForm(forms.ModelForm):
    body = forms.CharField(label="", max_length=300)
    image = forms.ImageField(required=False)

    class Meta:
        model = MessageModel

        fields = ['body', 'image']


class ShareForm(forms.Form):
    body = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'rows': '2', 'placeholder': 'Say Something...'})
    )


class ExploreForm(forms.Form):
    auery = forms.CharField(label="", widget=forms.TextInput(attrs={'placehoder': 'Explore tags'}))
