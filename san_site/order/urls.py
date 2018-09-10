from django.conf.urls import url

from san_site.order import views

urlpatterns = [
    url(r'(?P<id>\d+)\/?$', views.order, name='order'),
    url(r'^create/$', views.order_create, name='order_create'),
    url(r'^list/$', views.order_list, name='order_list'),
]
