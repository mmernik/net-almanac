from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

if settings.PRODUCTION:
    urlpatterns = patterns('',
        (r'', include('almanac.net_almanac.urls')),
    )
else:
    urlpatterns = patterns('',
    
    (r'^net_almanac/', include('almanac.net_almanac.urls')),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'media'}),

    )
