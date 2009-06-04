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
    
    (r'^create/$',
     'django.views.generic.create_update.create_object',
     {'form_class':EventForm}),
    
    (r'^tag/$', 'django.views.generic.list_detail.object_list',
        {'template_name':'event/tag_list.html',
         'queryset':Tag.objects.all()}),
         
    (r'^tag/(?P<tag_name>\w+)/$',
      'almanac.event.views.tag')
    
    
)
