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
    logger = logging.getLogger('view tag')
    
    logger.debug('hit')
    tag = Tag.objects.get(id=tag_id)
    events = TaggedItem.objects.get_by_model(Event,tag)
    
    return render_to_response('event/tag_detail.html',
                              {'tag':tag,
                               'events':events})
    
    
def create_event(request):
    logger = logging.getLogger('view create_event')
    
    logger.info('hit')
    
    logger.info('request.method='+request.method)
    
    form = EventForm()
    
    events = Event.objects.all()
    if request.method == 'GET':
        return render_to_response('event/event_form.html',
                                  {'form':form,
                                   'form_table':form.as_table()})       

        
    elif request.method == 'POST':
        
        try:
            logger.info('trying to create new event...')
            post_data = request._get_post()
            validate_post(post_data)
            
            new_event = Event(name=post_data['name'],
                              description=post_data['description'],
                              begin_time=post_data['begin_time'],
                              end_time=post_data['end_time'],
                              url=post_data['url'],
                              router=post_data['router'],
                              iface=post_data['iface'])
            
            
            logger.info('trying to save new event...')
            new_event.save()
            logger.info('save successful! event added: ' + new_event.name)
            
            logger.info('setting tags on new event')
            new_event.tags=post_data['tags']
            return HttpResponseRedirect('/event/')
        
        
        except ValueError, e:
            #TODO: include old user input
            logger.info('bad user input')
            return render_to_response('event/event_form.html',
                                      {'form':form,
                                       'form_table':form.as_table(),
                                       'error':e.message})
        
        except Exception, e:
            
            error_message = (str(type(e)) + ': ' +
                             e.message)
            
            logger.info(error_message)
            return render_to_response('event/event_form.html',
                                      {'form':form,
                                       'form_table':form.as_table(),
                                       'error':error_message})
        else:
            logger.error('unexpected error!')
            
        
def update_event(request,object_id):
    
    logger = logging.getLogger('view update_event')
    logger.info('hit')
    
    logger.info('request.method='+request.method)
    
    event = Event.objects.get(id=object_id)
    events = Event.objects.all()
    if request.method == 'GET':

        form = EventForm(instance=event)
        return render_to_response('event/event_form.html',
                                  {'form':form,
                                   'form_table':form.as_table()})       

        
    elif request.method == 'POST':
        
        return render_to_response('event/event_list.html',
                                  {'object_list':events})
        
def validate_post(post_data):
    if post_data['name']=='':
        raise ValueError('name cannot be empty')
    if post_data['description']=='':
        raise ValueError('description cannot be empty')
    if post_data['url']=='':
        raise ValueError('url cannot be empty')
    if post_data['iface']=='':
        raise ValueError('iface cannot be empty')
    if post_data['router']=='':
        raise ValueError('router cannot be empty')
    
    
    
    
    
    
    
