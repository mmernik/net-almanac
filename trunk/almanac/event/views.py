from django.http import Http404
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404

from almanac.event.models import *
from tagging.models import *

import logging
import datetime
import dateutil.parser

def tag(request,tag_id):
    logger = logging.getLogger('view tag')
    
    logger.debug('hit')
    tag = Tag.objects.get(id=tag_id)
    events = TaggedItem.objects.get_by_model(Event,tag)
    
    return render_to_response('event/tag_detail.html',
                              {'tag':tag,
                               'events':events})
    
    
def create_event(request):
    #a GET request returns a new form, and a POST request attempts to create a new event
    logger = logging.getLogger('view create_event')
    
    logger.info('hit')
    logger.debug('request.method='+request.method)
    form = EventForm()
    
    if request.method == 'GET':
        return render_to_response('event/event_form.html',
                                  {'type': 'Create',
                                   'form':form,
                                   'form_table':form.as_table()})
        
    elif request.method == 'POST':
        
        try:
            logger.debug('trying to create new event...')
            post_data = request._get_post()
            validate_post(post_data)
            
            begin_datetime_string = post_data['begin_date'] + ' ' + post_data['begin_time']
            end_datetime_string = post_data['end_date'] + ' ' + post_data['end_time']
            
            
            new_event = Event(name=post_data['name'],
                              description=post_data['description'],
                              begin_datetime=dateutil.parser.parse(begin_datetime_string),
                              end_datetime=dateutil.parser.parse(end_datetime_string),
                              url=post_data['url'],
                              router=post_data['router'],
                              iface=post_data['iface'])
            
            
            logger.debug('trying to save new event...')
            new_event.save()
            logger.info('save successful! event added: ' + new_event.name)
            
            logger.debug('setting tags on new event')
            new_event.tags=post_data['tags']
            return HttpResponseRedirect('/event/')
        
        except Exception, e:
            
            error_message = (str(type(e)) + ': ' +
                             e.message)
            
            logger.warning(error_message)
            return render_to_response('event/event_form.html',
                                      {'type':'Create',
                                       'form':form,
                                       'form_table':form.as_table(),
                                       'error':error_message})
        else:
            logger.error('unexpected error!')
            
        
def update_event(request,object_id):
    #a GET request returns a new form, and a POST request attempts to edit an event
    logger = logging.getLogger('view update_event')
    
    logger.info('hit')
    logger.debug('request.method='+request.method)
    
    event = get_event_by_id(object_id)
    if event == None:
        raise Http404
    
    form = EventForm(instance=event)
    
    if request.method == 'GET':
        
        
        return render_to_response('event/event_form.html',
                                  {'type': 'Update',
                                   'form':form,
                                   'form_table':form.as_table()})       

        
    elif request.method == 'POST':
        
        try:
            logger.debug('trying to update an event ' + event.name)
            post_data = request._get_post()
            validate_post(post_data)
            
            event.name = post_data['name']
            event.description = post_data['description']
            event.url = post_data['url']
            event.router = post_data['router']
            event.iface = post_data['iface']
            
            begin_datetime_string = post_data['begin_date'] + ' ' + post_data['begin_time']
            event.begin_datetime = dateutil.parser.parse(begin_datetime_string)
            
            end_datetime_string = post_data['end_date'] + ' ' + post_data['end_time']
            event.end_datetime = dateutil.parser.parse(end_datetime_string)
            
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
        
def delete_event(request,object_id):
    #a GET request gives a confirmation page, and a POST request deletes and redirects
    logger = logging.getLogger('view delete_event')
    
    logger.info('hit')
    logger.debug('request.method='+request.method)
    
    event = get_event_by_id(object_id)
    if event == None:
        raise Http404
    
    if request.method == 'GET':
        
        return render_to_response('event/event_confirm_delete.html',
                                  {'event':event,})
        
    elif request.method == 'POST':
        logger.debug('deleting event: ' + event.name)
        
        #we need to delete tags because they are not automatically deleted with delete()
        event.tags = ""
            
        event.delete()
        
        logger.info('delete successful! event delete: ' + event.name)
        
        return HttpResponseRedirect('/event/')
    

def validate_post(post_data):
    logger = logging.getLogger('validate_post')
    logger.debug('checking data')
    
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
    
    try:
        begin_datetime_string = post_data['begin_date'] + ' ' + post_data['begin_time']
        d = dateutil.parser.parse(begin_datetime_string)
    except:
        raise ValueError('invalid date format for begin date')
    
    try:
        end_datetime_string = post_data['end_date'] + ' ' + post_data['end_time']
        d = dateutil.parser.parse(end_datetime_string)
    except:
        raise ValueError('invalid date format for begin date')
    
def get_event_by_id(event_id):
    #returns an event or None if none exists.
    try:
        event = Event.objects.get(id=event_id)
        return event
    except:
        return None