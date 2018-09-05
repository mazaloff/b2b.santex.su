from django.conf.urls import url
from san_site.ajax import views_ajax as views

urlpatterns = [
    url(r'get_categories$', views.get_categories, name='get_categories'),
    url(r'get_goods/$', views.get_goods, name='get_goods'),
    url(r'cart_add/$', views.cart_add, name='cart_add'),
    url(r'cart_add_quantity/$', views.cart_add_quantity, name='cart_add_quantity'),
    url(r'cart_reduce_quantity/$', views.cart_reduce_quantity, name='cart_reduce_quantity'),
]
