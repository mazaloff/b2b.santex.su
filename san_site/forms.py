from django import forms
from san_site.models import Order
from django.conf import settings

class LoginForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class PasswordResetForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)


class PasswordChangeForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Текущий')
    password_new = forms.CharField(widget=forms.PasswordInput, label='Новый')
    password_repeat = forms.CharField(widget=forms.PasswordInput, label='Повтор')


class OrderCreateForm(forms.ModelForm):
    delivery = forms.DateField(widget=forms.SelectDateWidget, label='Срок поставки')
    shipment = forms.ChoiceField(choices=settings.SHIPMENT_TYPE, required=True,
                                 initial=settings.SHIPMENT_TYPE[0], label='Способ доставки')
    payment = forms.ChoiceField(choices=settings.PAYMENT_FORM, required=True,
                                 initial=settings.PAYMENT_FORM[0], label='Форма оплаты')
    comment = forms.CharField(widget=forms.Textarea, label='Комментарий')

    class Meta:
        model = Order
        fields = ['delivery', 'shipment', 'payment', 'comment']
