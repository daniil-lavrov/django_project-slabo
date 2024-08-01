from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import User, Challenges

class UserRegistrationForm(UserCreationForm):
        email = forms.EmailField(required=True)
        city = forms.CharField(max_length=100, required=False)
        nick = forms.CharField(max_length=100, required=False)

        class Meta:
            model = User
            fields = ['email', 'first_name', 'last_name', 'city', 'password1', 'password2', 'nick']

class ChallCreatingForm(forms.ModelForm):
    class Meta:
        model = Challenges
        fields = ['title', 'descr', 'duration', 'added_friend']




