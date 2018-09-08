from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, PasswordChangeForm, PasswordResetForm, OrderCreateForm
from django.contrib.auth.models import User
from san_site.models import Person, Order, OrderItem
from san_site.cart.cart import Cart
from django.contrib import messages


def index(request):
    return render(request, 'content.html', {})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    try:
                        customer = Person.objects.get(user=user)
                        if not customer.change_password:
                            form = PasswordChangeForm()
                            return render(request, 'account/password_change.html',
                                   {'form': form, 'change_password': True})
                    except Person.DoesNotExist:
                        pass
                    return index(request)
                else:
                    messages.error(request, 'Имя пользователя и пароль не совпадают. Попробуйте еще раз.')
                    return render(request, 'account/login.html', {'form': form})
            else:
                messages.error(request, 'Имя пользователя и пароль не совпадают. Попробуйте еще раз.')
                return render(request, 'account/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def user_logout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
    return index(request)


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = PasswordResetForm()
    return render(request, 'account/password_reset.html', {'form': form, 'errors': False})


def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                cd = form.cleaned_data
                if request.user.check_password(cd['password']):
                    user = User.objects.get(id=request.user.id)
                    user.set_password(cd['password_new'])
                    user.save()
                    try:
                        customer = Person.objects.get(user=user)
                        customer.change_password = True
                        customer.save()
                    except Person.DoesNotExist:
                        pass
                    login(request, user)
                    return render(request, 'account/password_change_done.html', {})
                else:
                    messages.error(request, 'Неверный текущий пароль.')
                    return render(request, 'account/password_change.html', {'form': form})
            else:
                messages.error(request, 'Новый пароль и повтор не совпадают.')
                return render(request, 'account/password_change.html', {'form': form})
        else:
            messages.error(request, 'Пользователь не авторизирован.')
            return render(request, 'account/password_change.html', {'form': form})

    form = PasswordChangeForm()
    return render(request, 'account/password_change.html', {'form': form})


def password_change_done(request):
    return render(request, 'account/password_change_done.html', {})


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            return render(request, 'orders/created.html',
                          {'order': order})
    else:
        form = OrderCreateForm
    cart_goods_list = cart.get_cart_list()
    cart_table_guids = [elem['guid'] for elem in cart_goods_list]
    return render(request, 'orders/create.html',{
                      'cart': cart,
                      'cart_goods_list': cart_goods_list,
                      'cart_table_guids': cart_table_guids,
                      'form': form}
                  )
