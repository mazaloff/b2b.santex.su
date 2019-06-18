from django.conf.urls import url

from san_site.ajax import views

urlpatterns = [
    url(r'get_categories$', views.get_categories, name='get_categories'),
    url(r'get_goods/$', views.get_goods, name='get_goods'),
    url(r'get_help_tip/$', views.get_help_tip, name='get_help_tip'),
    url(r'selection/$', views.selection, name='selection'),
    url(r'goods/get_form_images/$', views.get_form_images, name='get_form_images'),
    url(r'cart/add/$', views.cart_add, name='cart_add'),
    url(r'cart/get_form_quantity/$', views.cart_get_form_quantity, name='cart_get_form_quantity'),
    url(r'cart/add_quantity/$', views.cart_add_quantity, name='cart_add_quantity'),
    url(r'cart/reduce_quantity/$', views.cart_reduce_quantity, name='cart_reduce_quantity'),
    url(r'cart/delete_row/$', views.cart_delete_row, name='cart_delete_row'),
    url(r'order/get_orders_list/$', views.get_orders_list, name='get_orders_list'),
]
