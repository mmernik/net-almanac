from django.conf.urls.defaults import *
from event.models import *

info_dict = {
    'queryset': Event.objects.all(),
}


urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list',info_dict),
)
