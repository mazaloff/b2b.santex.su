from django.conf.urls import url
from san_site.api.views_api import api_upsert, api_inventories, api_prices


urlpatterns = [
    url(r'upsert$', api_upsert, name='api_upsert'),
    url(r'inventories$', api_inventories, name='api_inventories'),
    url(r'prices$', api_prices, name='api_prices'),
]