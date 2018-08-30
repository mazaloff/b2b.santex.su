from django.conf.urls import url
from . import views
from django.urls import include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/v1/', include('san_site.api.urls_api')),
    url(r'^ajax/', include('san_site.ajax.urls_ajax')),

]