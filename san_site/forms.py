import datetime

from django.utils import timezone
from django import forms
from django.conf import settings

from san_site.cart.cart import Cart, Currency
from san_site.models import Order, OrderItem, Person
import pytz


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
    delivery = forms.DateTimeField(
        widget=forms.SelectDateWidget,
        initial=datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + datetime.timedelta(days=1),
        label='Срок поставки')
    shipment = forms.ChoiceField(choices=settings.SHIPMENT_TYPE, required=True,
                                 initial=settings.SHIPMENT_TYPE[0], label='Способ доставки')
    payment = forms.ChoiceField(choices=settings.PAYMENT_FORM, required=True,
                                initial=settings.PAYMENT_FORM[1], label='Форма оплаты')
    comment = forms.CharField(widget=forms.Textarea, label='Комментарий к заказу', required=False)

    class Meta:
        model = Order
        fields = ['delivery', 'shipment', 'payment', 'comment']

    def clean_delivery(self):
        now = datetime.date.today()
        if self.cleaned_data['delivery'].date() < now:
            raise forms.ValidationError(
                "Срок поставки больше текущей даты."
            )
        return self.cleaned_data['delivery']

    def clean(self):
        pass

    def save(self, commit=True, **kwargs):
        request = kwargs.get('request', None)
        if request is None:
            return
        person = None
        set_person = Person.objects.filter(user=request.user)
        if len(set_person) > 0:
            person = set_person[0]
        eastern = pytz.timezone(settings.TIME_ZONE)
        delivery = self.cleaned_data['delivery'].astimezone(tz=eastern)
        order = Order.objects.create(
            person=person,
            delivery=delivery,
            shipment=self.cleaned_data['shipment'],
            payment=self.cleaned_data['payment'],
            comment=self.cleaned_data['comment']
        )
        order.save()

        cart = Cart(request)
        for item in cart:
            try:
                currency = Currency.objects.get(id=item['currency_id'])
            except Currency.DoesNotExist:
                currency = None
                pass
            item = OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                price_ruble=item['price_ruble'],
                quantity=item['quantity']
            )
            if currency:
                item.currency = currency
            item.save()
        cart.clear()

        order.save()
        order.request_order()

        return order
