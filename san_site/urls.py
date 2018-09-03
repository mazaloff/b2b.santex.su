from django.conf.urls import url
from . import views
from django.urls import include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.user_login, name='account_login'),
    url(r'^logout/$', views.user_logout, name='account_logout'),
    url(r'^login/password_reset/$', views.password_reset, name='account_password_reset'),
    url(r'^login/password_change/$', views.password_change, name='account_password_change'),
    url(r'^login/password_change_done/$', views.password_change_done, name='account_password_change_done'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^api/', include('san_site.api.urls_api')),
    url(r'ajax/', include('san_site.ajax.urls_ajax')),
]
