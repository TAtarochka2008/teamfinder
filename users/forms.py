from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profile


User = get_user_model()


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower()
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

    def clean_username(self):
        return self.cleaned_data["username"].lower()


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)
    email = forms.EmailField(label="Email")

    class Meta:
        model = Profile
        fields = ("avatar_url", "bio", "phone", "github")
        labels = {
            "avatar_url": "Ссылка на аватар",
            "bio": "О себе",
            "phone": "Телефон",
            "github": "GitHub",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["email"].initial = user.email

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        users = User.objects.filter(email=email).exclude(pk=self.instance.user_id)
        if users.exists():
            raise forms.ValidationError("Этот email уже занят.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"].lower()
        user.username = self.cleaned_data["email"].lower()
        if commit:
            user.save()
            profile.save()
        return profile
