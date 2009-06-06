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
    
    logger.debug('request.method='+request.method)
    
    form = EventForm()
    
    events = Event.objects.all()
    if request.method == 'GET':
        return render_to_response('event/event_form.html',
                                  {'form':form,
                                   'form_table':form.as_table()})       

        
    elif request.method == 'POST':
        
        try:
            logger.debug('trying to create new event...')
            post_data = request._get_post()
            validate_post(post_data)
            
            new_event = Event(name=post_data['name'],
                              description=post_data['description'],
                              begin_time=post_data['begin_time'],
                              end_time=post_data['end_time'],
                              url=post_data['url'],
                              router=post_data['router'],
                              iface=post_data['iface'])
            
            
            logger.debug('trying to save new event...')
            new_event.save()
            logger.info('save successful! event added: ' + new_event.name)
            
            logger.debug('setting tags on new event')
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
            
            logger.warning(error_message)
            return render_to_response('event/event_form.html',
                                      {'form':form,
                                       'form_table':form.as_table(),
                                       'error':error_message})
        else:
            logger.error('unexpected error!')
            
        
def update_event(request,object_id):
    logger = logging.getLogger('view update_event')
    
    logger.info('hit')
    logger.debug('request.method='+request.method)
    
    event = Event.objects.get(id=object_id)
    form = EventForm(instance=event)
    #We need to manually set tags.
    form.initial['tags'] = tagging.utils.edit_string_for_tags(event.tags)
    if request.method == 'GET':
        
        
        return render_to_response('event/event_form.html',
                                  {'form':form,
                                   'form_table':form.as_table()})       

        
    elif request.method == 'POST':
        
        try:
            logger.debug('trying to update an event...')
            post_data = request._get_post()
            validate_post(post_data)
            
            event.name = name=post_data['name']
            event.description = description=post_data['description']
            event.begin_time = begin_time=post_data['begin_time']
            event.end_time = end_time=post_data['end_time']
            event.url = url=post_data['url']
            event.router = router=post_data['router']
            event.iface = iface=post_data['iface']
            
            
            logger.debug('trying to save event...')
            event.save()
            logger.info('save successful! event updated: ' + event.name)
            
            logger.debug('setting tags on updated event')
            event.tags=post_data['tags']
            
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
    
    
    
    
    
    
    
