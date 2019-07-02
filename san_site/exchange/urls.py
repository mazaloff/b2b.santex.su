from django.conf.urls import url

from san_site.exchange import views

urlpatterns = [
    url(r'api/v1/main$', views.api_main, name='api_main'),
    url(r'api/v1/photo_of_good$', views.api_photo_of_good, name='api_photo_of_good'),
    url(r'api/v1/bill_of_order$', views.bill_of_order, name='bill_of_order'),
    url(r'api/v1/inventories$', views.api_inventories, name='api_inventories'),
    url(r'api/v1/prices$', views.api_prices, name='api_prices'),
    url(r'api/v1/users$', views.api_users, name='api_users'),
    url(r'api/v1/courses$', views.api_courses, name='api_courses'),
    url(r'api/v1/users_prices$', views.api_users_prices, name='api_users_prices'),
    url(r'api/v1/statuses$', views.api_statuses, name='api_statuses'),
]
