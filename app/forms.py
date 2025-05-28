from django import forms
from django.contrib.auth.models import User

from app.models import Profile, Tag


class RegisterForm(forms.Form):
    username = forms.CharField(label='Login', max_length=30)
    email = forms.EmailField(label='Email', max_length=50)
    nickname = forms.CharField(label='Nickname', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=30)
    passwordr = forms.CharField(widget=forms.PasswordInput, label='Passwordr', max_length=30)
    avatar = forms.ImageField(label='Avatar', required=False)
    accept = forms.BooleanField(label='Accept', required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).first()
        if user is not None:
            raise forms.ValidationError('Username already taken')
        return username

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        profile = Profile.objects.filter(nickname=nickname).first()
        if profile is not None:
            raise forms.ValidationError('Nickname already taken')
        return nickname

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters")
        return password

    def clean_passwordr(self):
        password = self.cleaned_data['passwordr']
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters")
        if password != self.cleaned_data['password']:
            raise forms.ValidationError("Passwords do not match")
        return password

    def clean_avatar(self):
        print(self.cleaned_data['avatar'])
        if self.cleaned_data['avatar']  is None:
            self.cleaned_data['avatar'] = "default.jpg"
        return self.cleaned_data['avatar']

    def clean_accept(self):
        if not self.cleaned_data['accept']:
            raise forms.ValidationError('Accept conditions!')
        return self.cleaned_data['accept']

    def save(self):
        user = User(username=self.cleaned_data['username'], email=self.cleaned_data['email'], )
        user.set_password(self.cleaned_data['password'])
        profile = Profile(nickname=self.cleaned_data['nickname'], avatar=self.cleaned_data['avatar'], user=user)
        user.save()
        profile.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(label="Login", max_length = 30)
    password = forms.CharField(max_length=30, widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters")
        return password


class SettingsForm(forms.Form):
    username = forms.CharField(label="Login", max_length = 30)
    email = forms.EmailField(max_length=50)
    nickname = forms.CharField(max_length = 30)
    avatar = forms.ImageField(required=False)


class AskForm(forms.Form):
    title = forms.CharField(label='Title', max_length=30)
    text = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(label='tags', widget=forms.TextInput(attrs={'placeholder': 'Введите теги через пробел...',}))

    def clean_tags(self):
        tags = list(filter(lambda s: len(s)>0, self.cleaned_data['tags'].split()))
        if len(tags) > 3:
            raise forms.ValidationError("Tags must be at least 3")
        for tag in tags:
            if len(tag) > 20:
                raise forms.ValidationError("Tag must be less than 20 characters")
            if len(tag) < 1:
                raise forms.ValidationError("Tag must be at least 1 character")
        return tags


class AnswerForm(forms.Form):
    text = forms.CharField(label="Написать комментарий", widget=forms.Textarea)

