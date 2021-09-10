from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordChangeForm(forms.Form):
    password = forms.CharField(label='Текущий пароль')
    password_new = forms.CharField(label='Новый пароль')
    password_new_done = forms.CharField(label='Новый пароль (повторно)')
