from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()



urlpatterns = patterns('',
    url(r'^$', 'sports.views.home'),
    url(r'^player/$', 'sports.views.allplayers'),
    url(r'^player/(?P<user_id>\d+)/$', 'sports.views.playerdetails'),
    url(r'^allteams/$', 'sports.views.allteams'),
    url(r'^team/(?P<team_id>\d+)/$', 'sports.views.teamdetails'),
    url(r'^team/(?P<team_id>\d+)/schedule/$', 'sports.views.matchups'),
    url(r'^login/$', 'sports.views.login'),
    url(r'^admin/$', 'sports.views.admin'),
    url(r'^addteams/$', 'sports.views.addteams'),
    url(r'^addteams/make/$', 'sports.views.maketeams'),
    url(r'^changeseason/$', 'sports.views.changeseason'),
    url(r'^changeseason/make/$', 'sports.views.change'),
    url(r'^logout/$', 'sports.views.logout'),
)

if settings.DEBUG is False:    #This is bad. It should probably be done using apache to serve the static files, future fix?
        urlpatterns += patterns('',
                            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/users/u20/tcohen/CSHSports/Templates/Static'}),
                                )
