from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class PasswordResetForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)


class PasswordChangeForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Текущий')
    password_new = forms.CharField(widget=forms.PasswordInput, label='Новый')
    password_repeat = forms.CharField(widget=forms.PasswordInput, label='Повтор')
