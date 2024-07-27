# chatbot_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ChatSessionForm(forms.Form):
    product_name = forms.CharField(max_length=255)
    num_articles = forms.IntegerField(min_value=1)

class ArticleForm(forms.Form):
    url = forms.URLField()

class ChatMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)