from django.conf.urls import url

from san_site.files import views

urlpatterns = [
    url(r'for_loading[/]?$', views.for_loading, name='files_for_loading'),
    url(r'^static/inventories[/](?P<name_file>\S+)', views.inventories),
    url(r'create', views.create, name='files_create'),
    url(r'^static/bills[/](?P<guid>\S+)', views.bill),
    url(r'^static[/](?P<id>\d+)[/](?P<name_file>\S+)', views.static),
]
