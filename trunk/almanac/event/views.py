from django.http import Http404
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404

from almanac.event.models import *
from tagging.models import *

import logging
import datetime

def tag(request,tag_id):
    logging.debug('view tag hit')
    tag = Tag.objects.get(id=tag_id)
    events = TaggedItem.objects.get_by_model(Event,tag)
    
    return render_to_response('event/tag_detail.html',
                              {'tag':tag,
                               'events':events})
    
    
def tag_update(request,object_id):
    logging.debug("view tag_update hit")
    
    event = Event.objects.get(id=object_id)
    
    return render_to_response('event/event_detail.html',
            {'object':event})
    
def create_event(request):
    logging.info('view create_event hit')
    
    logging.info('request.method='+request.method)
    
    if request.method == 'GET':

        form = EventForm()
        return render_to_response('event/event_form.html',
                                  {'form':form,
                                   'form_table':form.as_table()})       

        
    elif request.method == 'POST':
        events = Event.objects.all()
        
        logging.debug(dir(request))
        
        logging.debug(request._get_post()['name'])
        
        post_data = request._get_post()
        
        new_event = Event(name=post_data['name'],
                          description=post_data['description'],
                          #TODO: get these later, maybe use Django input widgets
                          #begin_time=post_data['begin_time'],
                          #end_time=post_data['end_time'],
                          
                          begin_time=datetime.datetime(2008,1,1),
                          end_time=datetime.datetime(2008,1,2),
                          url=post_data['url'],
                          router=post_data['router'],
                          iface=post_data['iface'])
        
        new_event.save()
        
        return render_to_response('event/event_list.html',
                                  {'object_list':events})
        
def update_event(request,object_id):
    logging.info('view update_event hit')
    
    logging.info('request.method='+request.method)
    
    event = Event.objects.get(id=object_id)
    
    if request.method == 'GET':

        form = EventForm(instance=event)
        return render_to_response('event/event_form.html',
                                  {'form':form,
                                   'form_table':form.as_table()})       

        
    elif request.method == 'POST':
        
        logging.debug(request._get_post()['name'])
        return render_to_response('event/event_list.html',
                                  {'object_list':events})
