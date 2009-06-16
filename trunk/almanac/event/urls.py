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
    #Default homepage displays a list.
    (r'^$', 
     'almanac.event.views.list_events'),
    
    #Various options for a specific event.
    (r'^(?P<object_id>\d+)/$', 
     'almanac.event.views.detail_event'),
    
    (r'^(?P<object_id>\d+)/update/$', 
     'almanac.event.views.update_event'),
     
    (r'^(?P<object_id>\d+)/delete/$', 
     'almanac.event.views.delete_event'),
    
    
    #Other stuff
    (r'^create/$',
     'almanac.event.views.create_event'),
    
    (r'^tag/$', 
     'almanac.event.views.tag_list'),
         
    (r'^tag/(?P<tag_id>\w+)/$',
      'almanac.event.views.tag'),
      
      
    #date-based views
    (r'^date/$',
     'almanac.event.views.view_by_date'),
    
    (r'^date/(?P<year>\d{4})/$',
     'almanac.event.views.view_by_year'),
     
    (r'^date/(?P<year>\d{4})/(?P<month>\d{2})/$',
     'almanac.event.views.view_by_month'),
    
)
