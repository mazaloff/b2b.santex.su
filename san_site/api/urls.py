from django.conf.urls import url

from san_site.api import views

urlpatterns = [
    url(r'v1/main$', views.api_main, name='api_main'),
    url(r'v1/photo_of_good$', views.api_photo_of_good, name='api_photo_of_good'),
    url(r'v1/inventories$', views.api_inventories, name='api_inventories'),
    url(r'v1/prices$', views.api_prices, name='api_prices'),
    url(r'v1/users$', views.api_users, name='api_users'),
    url(r'v1/courses$', views.api_courses, name='api_courses'),
    url(r'v1/users_prices$', views.api_users_prices, name='api_users_prices'),
    url(r'v1/statuses', views.api_statuses, name='api_statuses'),
    url(r'v1/outside[/]$', views.outside, name='outside'),
    url(r'our_api$', views.our_api, name='our_api'),
]
