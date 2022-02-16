from django.conf.urls import url

from . import views

urlpatterns = [
    url('v1/login[/]?$', views.login, name='rest_login'),
    url('v1/products[/]?$', views.ProductListView.get, name='rest_products'),
    url('v1.1/products[/]?$', views.ProductListViewV1.get, name='rest_products_v1'),
    url('v1.1/orders[/]?$', views.OrderListView.get, name='rest_orders'),
    url('v1.1/bills[/]?$', views.BillListView.get, name='rest_orders'),
    url('v1/catalog[/]?$', views.CatalogView.get, name='rest_catalog'),
    url(r'our_api[/]?$', views.our_api, name='our_api'),
]
