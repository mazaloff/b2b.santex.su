from django.conf.urls import url

from . import views

urlpatterns = [
    url('v1/login[/]?$', views.login),
    url('v1/products[/]?$', views.ProductListView.get),
    url('v1.1/products[/]?$', views.ProductListViewV1.get),
    url('v1.1/orders[/]?$', views.OrderListView.get),
    url('v1.1/bills[/]?$', views.BillListView.get),
    url('v1.1/users[/]?$', views.UserListView.get),
    url('v1/catalog[/]?$', views.CatalogView.get),
    url(r'our_api[/]?$', views.our_api, name='our_api'),
]
