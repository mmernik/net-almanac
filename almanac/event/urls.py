from django.conf.urls.defaults import *
from event.models import *
from tagging.models import *

info_dict = {
    'queryset': Event.objects.all(),
}

tags_dict = {
    'queryset':Tag.objects.all()
}


urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list',info_dict),
    (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict),
    
    (r'^(?P<object_id>\d+)/update/$', 
     'almanac.event.views.update_event'),
    
    (r'^(?P<object_id>\d+)/tag_update/$',
     'almanac.event.views.tag_update'),
    
    (r'^create/$',
     'almanac.event.views.create_event'),
    
    (r'^tag/$', 'django.views.generic.list_detail.object_list',
        {'template_name':'event/tag_list.html',
         'queryset':Tag.objects.all()}),
         
    (r'^tag/(?P<tag_id>\w+)/$',
      'almanac.event.views.tag')
    
    
    
)
