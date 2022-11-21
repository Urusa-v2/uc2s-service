from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Groups

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','email','group')
        exclude = ('isleader',)

class LeaderSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','email')
        exclude = ('isleader','group',)

class LoginAuthForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username','password')

class groupForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ('name',)