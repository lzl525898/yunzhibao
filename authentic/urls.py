from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^login/$', 'authentic.views.user_login', name='login'),
    url(r'^logout/$', 'authentic.views.user_logout', name='logout'),
)
