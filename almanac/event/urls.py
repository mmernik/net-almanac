from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'almanac.event.views.index'),
)
