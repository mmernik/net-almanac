from django.http import Http404
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404

from almanac.event.models import Event

import logging

def index(request):
    
    logging.info('index hit')
    h = render_to_response('event/index.html',{'events':Event.objects.all()})
    return h