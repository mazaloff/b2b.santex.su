from django.conf.urls import url
from san_site.ajax import views_ajax as views

urlpatterns = [
    url(r'get_categories$', views.get_categories, name='get_categories'),
    url(r'get_goods/$', views.get_goods, name='get_goods'),
    url(r'add/$', views.cart_add, name='cart_add'),
    url(r'remove/$', views.cart_remove, name='cart_remove'),
]
