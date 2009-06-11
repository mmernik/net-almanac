from django.http import Http404
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404

from almanac.event.models import *
from tagging.models import *

import logging
import datetime
import dateutil.parser
import tagging

JSON_MIME = 'application/json'

def tag(request,tag_id):
    logger = logging.getLogger('view tag')
    
    logger.debug('hit')
    tag = Tag.objects.get(id=tag_id)
    events = TaggedItem.objects.get_by_model(Event,tag)
    
    return render_to_response('event/tag_detail.html',
                              {'tag':tag,
                               'events':events})
    

def list_events(request):
    logger = logging.getLogger('view list_events')
    
    logger.info('hit')
    
    events = Event.objects.all()
    
    if is_json_request(request):
        #return serialized objects.
        logger.debug('request for json list of all objects')
        json_data = serializers.serialize('json',events)
        return HttpResponse(json_data,mimetype=JSON_MIME)
    else:
        return render_to_response('event/event_list.html',
                                  {'event_list':events})

def create_event(request):
    #a GET request returns a new form, and a POST request attempts to create a new event
    logger = logging.getLogger('view create_event')
    
    logger.info('hit')
    logger.debug('request.method='+request.method)
    form = EventForm()
    
    if request.method == 'GET':
        return render_to_response('event/event_create.html',
                                  {'form':form,
                                   'form_table':form.as_table()})
        
    elif request.method == 'POST':
        
        try:
            logger.debug('trying to create new event...')
            post_data = request._get_post()
            
            form = EventForm(request.POST)
            if form.is_valid():
                logger.debug('form is valid')
            else:
                logger.debug('form is not valid')
            validate_post(post_data)
            
            begin_datetime_string = post_data['begin_date'] + ' ' + post_data['begin_time']
            end_datetime_string = post_data['end_date'] + ' ' + post_data['end_time']
            
            tags_string = format_tag_string(post_data['tags'])
            
            new_event = Event(name=post_data['name'],
                              description=post_data['description'],
                              begin_datetime=dateutil.parser.parse(begin_datetime_string),
                              end_datetime=dateutil.parser.parse(end_datetime_string),
                              url=post_data['url'],
                              router=post_data['router'],
                              iface=post_data['iface'],
                              tags = tags_string)
            
            
            logger.debug('trying to save new event...')
            new_event.save()
            logger.info('save successful! event added: ' + new_event.name)
            
            return HttpResponseRedirect('/event/' + str(new_event.id))
        
        except ValueError, e:
            
            error_message = (str(type(e)) + ': ' +
                             e.message)
            
            logger.info(error_message)
            return render_to_response('event/event_create.html',
                                      {'form':form,
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
    
    form = EventForm(instance=event)
    
    if is_json_request(request):
        logger.debug('request for json object')
        return HttpResponse('some json data',mimetype=JSON_MIME)
    
    elif request.method == 'GET':
        return render_to_response('event/event_update.html',
                                  {'event': event,
                                   'form':form,
                                   'form_table':form.as_table()})       
        
    elif request.method == 'POST':
        try:
            logger.debug('trying to update an event ' + event.name)
            post_data = request._get_post()
            
            form = EventForm(request.POST)
            if form.is_valid():
                logger.debug('form is valid')
            else:
                logger.debug('form is not valid')
            
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
            
            event.tags = format_tag_string(post_data['tags'])
            
            logger.debug('trying to save event...')
            event.save()
            logger.info('save successful! event updated: ' + event.name)
            
            logger.debug('setting tags on updated event')
            event.tags=post_data['tags']
            
            return HttpResponseRedirect('/event/' + str(event.id))
        
        
        except ValueError, e:
            #TODO: include old user input
            logger.info('bad user input')
            error_message = (str(type(e)) + ': ' +
                             e.message)
            return render_to_response('event/event_update.html',
                                      {'event': event,
                                       'form':form,
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

def detail_event(request,object_id):
    #displays data about one object.  
    logger = logging.getLogger('view detail_event')
    logger.info('hit')
    event = get_event_by_id(object_id)
    logger.debug('requesting data for event: ' + event.name)
    
    if is_json_request(request):
        logger.debug('request for individual json object')
        json_data = serializers.serialize('json',[event])
        logger.debug('serialized object: ' + json_data)
        return HttpResponse(json_data, mimetype=JSON_MIME)
    
    else:
        return render_to_response('event/event_detail.html',
                                  {'event':event,
                                   'tags':Tag.objects.get_for_object(event)})

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
    
    begin_datetime = None
    end_datetime = None
    
    try:
        begin_datetime_string = post_data['begin_date'] + ' ' + post_data['begin_time']
        begin_datetime = dateutil.parser.parse(begin_datetime_string)
    except:
        raise ValueError('invalid date format for begin date')
    
    try:
        end_datetime_string = post_data['end_date'] + ' ' + post_data['end_time']
        end_datetime = dateutil.parser.parse(end_datetime_string)
    except:
        raise ValueError('invalid date format for begin date')
    
    if end_datetime < begin_datetime:
        raise ValueError('the end date is before the begin date')
    
    for tag in tagging.utils.parse_tag_input(post_data['tags']):
        if tag.find(',') != -1:
            raise ValueError('a tag may not contain a comma')
    
def get_event_by_id(event_id):
    #returns an event or None if none exists.
    logger = logging.getLogger('get_event_by_id')
    event = None
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise Http404
    except Event.MultipleObjectsReturned:
        logger.error('unexpected error raised: multiple objects have one id')
        raise Http404 
    return event
    
def is_json_request(request):
    logger = logging.getLogger('is_json_request')
    
    if request.META.has_key('HTTP_ACCEPT'):
        logger.info('request.META["HTTP_ACCEPT"]: ' + request.META["HTTP_ACCEPT"])
        return (request.META["HTTP_ACCEPT"].find(JSON_MIME) != -1)
    else:
        logger.warn('request has no header HTTP_ACCEPT')
        return False
 
def format_tag_string(tags_string):
    logger = logging.getLogger('format_tag_string')
    return ', '.join(tagging.utils.parse_tag_input(tags_string))