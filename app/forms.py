from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
import imghdr


class CustomLoginView(LoginView):
    template_name = 'Login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        return '/'


def validate_image(value):
    valid_extensions = ["jpeg", "jpg", "png", "gif", "bmp", "webp"]
    extension = imghdr.what(value)

    if extension not in valid_extensions:
        raise ValidationError("Можно загружать только изображения (JPEG, PNG, GIF, BMP, WebP).")


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    nickname = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    repeat_password = forms.CharField(widget=forms.PasswordInput, required=True)
    avatar = forms.ImageField(required=True, validators=[validate_image])

    def clean_repeat_password(self):
        password = self.cleaned_data.get('password')
        repeat_password = self.cleaned_data.get('repeat_password')
        if password != repeat_password:
            raise ValidationError('Пароли не совпадают.')
        return repeat_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Этот логин уже занят.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Этот email уже зарегистрирован.')
        return email


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=True, validators=[validate_image])

    class Meta:
        model = User
        fields = ['username', 'email']
