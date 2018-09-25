from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, reverse
from django.http import Http404
from django.conf import settings

from .decorates.decorate import page_not_access
from .models import Person
from .forms import LoginForm, PasswordChangeForm, PasswordResetForm
from .tasks import letter_password_change as task_letter_password_change


@page_not_access
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
            cd = form.cleaned_data
            email = cd['email']
            set_query = User.objects.filter(email=email)
            if len(set_query) == 0:
                messages.error(request, 'Не найден акаунт с таким email.')
                return render(request, 'account/password_reset.html', {'form': form})
            try:
                person = set_query[0].person
            except Person.DoesNotExist:
                messages.error(request, 'Не найден акаунт с таким email.')
                return render(request, 'account/password_reset.html', {'form': form})

            url = request.build_absolute_uri(reverse('account_password_change'))

            if settings.CELERY_NO_SEND_EMAIL:
                person.letter_password_change(url)
            else:
                task_letter_password_change.delay(set_query[0].id, url)
            return render(request, 'account/password_reset_done.html', {})
    else:
        form = PasswordResetForm()
    return render(request, 'account/password_reset.html', {'form': form, 'errors': False})


def password_change_key(request, **kwargs):
    if request.method == 'POST':
        return password_change(request)
    else:
        key = kwargs.get('key', '').replace('/', '')
        try:
            person = Person.objects.get(key=key)
        except Person.DoesNotExist:
            raise Http404()
        try:
            user = person.user
        except User.DoesNotExist:
            raise Http404()
        login(request, user)
        form = PasswordChangeForm()
        form.fields['password'].disabled = True
        form.base_fields['password'].required = False
        return render(request, 'account/password_change.html', {'form': form})


@page_not_access
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                cd = form.cleaned_data
                if not form.fields['password'].required \
                        or request.user.check_password(cd['password']):
                    user = User.objects.get(id=request.user.id)
                    user.set_password(cd['password_new'])
                    user.save()
                    try:
                        person = Person.objects.get(user=user)
                        person.change_password = True
                        person.key = ''
                        person.save()
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
    form.base_fields['password'].required = True
    return render(request, 'account/password_change.html', {'form': form})


@page_not_access
def password_change_done(request):
    return render(request, 'account/password_change_done.html', {})
