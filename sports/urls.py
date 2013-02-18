from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^player/$', 'sports.views.allplayers'),
    url(r'^player/(?P<user_id>\d+)/$', 'sports.views.playerdetails'),
    url(r'^$', 'sports.views.allteams'),
    url(r'^team/(?P<team_id>\d+)/$', 'sports.views.teamdetails'),

)