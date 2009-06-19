from django.conf.urls.defaults import *
from net_almanac.models import *
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
     'almanac.net_almanac.views.root'),
    
    (r'^event/$', 
     'almanac.net_almanac.views.list_events'),
    
    #Various options for a specific event.
    (r'^event/(?P<object_id>\d+)/$', 
     'almanac.net_almanac.views.detail_event'),
    
    (r'^event/(?P<object_id>\d+)/update/$', 
     'almanac.net_almanac.views.update_event'),
     
    (r'^event/(?P<object_id>\d+)/delete/$', 
     'almanac.net_almanac.views.delete_event'),
    
    
    #Other stuff
    (r'^event/create/$',
     'almanac.net_almanac.views.create_event'),
    
    (r'^event/tag/$', 
     'almanac.net_almanac.views.tag_list'),
    
    (r'^event/tag/clean/$', 
     'almanac.net_almanac.views.tag_clean'),
         
    (r'^event/filter/$',
      'almanac.net_almanac.views.filter'),
      
    #date-based views
    (r'^event/date/$',
     'almanac.net_almanac.views.view_by_date'),
    
    (r'^event/date/(?P<year>\d{4})/$',
     'almanac.net_almanac.views.view_by_year'),
     
    (r'^event/date/(?P<year>\d{4})/(?P<month>\d{2})/$',
     'almanac.net_almanac.views.view_by_month'),
    
)
