from django.conf.urls import url
from san_site.api import views_api as views


urlpatterns = [
    url(r'v1/upsert$', views.api_upsert, name='api_upsert'),
    url(r'v1/inventories$', views.api_inventories, name='api_inventories'),
    url(r'v1/prices$', views.api_prices, name='api_prices'),
    url(r'v1/users$', views.api_users, name='api_users'),
    url(r'v1/courses$', views.api_courses, name='api_courses'),
    url(r'v1/users_prices$', views.api_users_prices, name='api_users_prices'),
]
