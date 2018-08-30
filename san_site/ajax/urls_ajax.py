from django.conf.urls import url
from san_site.ajax.views_ajax import get_categories, get_goods


urlpatterns = [
    url(r'get_categories$', get_categories, name='get_categories'),
    url(r'get_goods$', get_goods, name='get_goods'),
]