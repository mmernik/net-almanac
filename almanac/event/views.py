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
TEXT_MIME = 'text/plain'

HTTP_BAD_REQUEST = 400
HTTP_NOT_IMPLEMENTED = 501

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
                raise ValueError('invalid data in form')
            
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
            
            validate_event(new_event) #raises ValueError
            
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
    
    if request.method == 'GET':
        return render_to_response('event/event_update.html',
                                  {'event': event,
                                   'form':form,
                                   'form_table':form.as_table()})       
        
    elif request.method == 'POST':
        try:
            logger.debug('trying to update an event ' + event.name)
            post_data = request._get_post()
            
            form = EventForm(request.POST)
            logger.debug(str(post_data.__class__))
            logger.debug(str(post_data))
            
            if form.is_valid():
                logger.debug('form is valid')
            else:
                logger.debug('form is not valid')
                raise ValueError('form is not valid')
            
            
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
            
            validate_event(event) #raises ValueError
            
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
        
        if request.method == 'GET':
            logger.debug('got GET request for individual json object')
            json_data = serializers.serialize('json',[event])
            #logger.debug('serialized object: ' + json_data)
            return HttpResponse(json_data, mimetype=JSON_MIME)
        elif request.method == 'PUT':
            logger.info('got PUT request')
            #logger.debug('request.raw_post_data: ' + request.raw_post_data)
            deserialized_event = None
            try:
                logger.debug('parsing json')
                deserialized_event = parse_json_request(request.raw_post_data)
                
                validate_event(deserialized_event) #raises ValueError
                
                if (deserialized_event.id != int(object_id)):
                    logger.debug('deserialized_event.id: ' + str(deserialized_event.id))
                    logger.debug('object_id: ' + str(object_id))
                    error_str = 'id does not match with request URL'
                    logger.info(error_str)
                    return make_bad_request_http_response(error_str)
                logger.debug('trying to save edited event...')
                deserialized_event.save()
                logger.info('event saved!')
                
            except ValueError, e:
                #bad format
                error_str = 'ValueError: ' + str(e)
                logger.info(error_str)
                return make_bad_request_http_response(error_str)
            except Exception, e:
                logger.error('unexpected exception encountered: ' + str(e))
            
            return HttpResponse('event updated',mimetype=TEXT_MIME)

        elif (request.method == 'DELETE'):
            
            
            logger.info('got DELETE request...deleting selected event: ' + event.name)
                   
            event.delete()
            
            return HttpResponse('event deleted',mimetype=TEXT_MIME) 
   
        elif (request.method =='POST'):
            #not implemented
            logger.debug('got POST request...dropping')
            return HttpResponse('POST not supported at this URL',mimetype=TEXT_MIME,status=HTTP_NOT_IMPLEMENTED) #'not implemented' status code

    
    else:
        return render_to_response('event/event_detail.html',
                                  {'event':event,
                                   'tags':Tag.objects.get_for_object(event)})
        


def view_by_year(request,year):
    logger = logging.getLogger('view view_by_year')
    logger.info('hit')
    year_int = int(year)
    event_list = Event.objects.filter(begin_datetime__year=year)
    logger.debug('event_list: ' + str(event_list))
    return render_to_response('event/event_by_year.html',
                              {'event_list':event_list,
                               'year':year,
                               'next_year':year_int+1,
                               'last_year':year_int-1,
                               })
    
def view_by_month(request,year,month):
    logger = logging.getLogger('view view_by_month')
    logger.info('hit')
    year_int = int(year)
    month_int = int(month)
    
    if (month_int < 1) or (month_int > 12):
        raise Http404
    
    next_month = None #strings with encoding YYYY/MM
    last_month = None
    
    if (month_int==12):
        next_month = str(year_int+1) + '/01'
    else:
        next_month = str(year_int) + '/' + extend_int_string(str(month_int+1))
        
    if (month_int==1):
        last_month = str(year_int-1) + '/12'
    else:
        last_month = str(year_int) + '/' + extend_int_string(str(month_int-1))
        
    logger.debug('next_month: ' + next_month)
        
    event_list = Event.objects.filter(begin_datetime__year=year_int,
                                      begin_datetime__month=month_int)
    
    logger.debug('event_list: ' + str(event_list))
    
    return render_to_response('event/event_by_month.html',
                              {'event_list':event_list,
                               'year':year,
                               'month':month,
                               'next_month':next_month,
                               'last_month':last_month,
                               })
        
def view_by_date(request):
    #default date view, direct to all events this year.
    return HttpResponseRedirect('/event/date/' + str(datetime.date.today().year) + '/')

def validate_event(event):
    """
    Always call this before saving an event!
    
    raises ValueError when there is some inconsistency
    """
    logger = logging.getLogger('validate_event')
    
    
    if (event.__class__ != Event):
        logger.info('object is not of type Event')
        raise ValueError('object is not of type Event')
    
    logger.debug('checking event with name: ' + event.name)
    
    if is_empty_or_space(event.name):
        raise ValueError('name cannot be empty')
    if is_empty_or_space(event.description):
        raise ValueError('description cannot be empty')
    if is_empty_or_space(event.url):
        raise ValueError('url cannot be empty')
    if is_empty_or_space(event.iface):
        raise ValueError('iface cannot be empty')
    if is_empty_or_space(event.router):
        raise ValueError('name router be empty')
    
    logger.debug('parsing tags')
    for tag in tagging.utils.parse_tag_input(event.tags):
        #normally commas are delimiters, but if they are between double-quotes they become tags
        if tag.find(',') != -1:
            raise ValueError('a tag may not contain a comma')
    
    logger.debug('checking datetime')
    if event.end_datetime < event.begin_datetime:
        raise ValueError('the end date is before the begin date')
    
def is_empty_or_space(input_string):
    return (input_string == None or input_string == '' or input_string.isspace())
    
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
        #logger.info('request.META["HTTP_ACCEPT"]: ' + request.META["HTTP_ACCEPT"])
        return (request.META["HTTP_ACCEPT"].find(JSON_MIME) != -1)
    else:
        logger.warn('request has no header HTTP_ACCEPT')
        return False
 
def format_tag_string(tags_string):
    """
    Takes in some user-inputted tag string and formats it into a pretty comma-delimited string.
    """
    logger = logging.getLogger('format_tag_string')
    return ', '.join(tagging.utils.parse_tag_input(tags_string))


def parse_json_request(json_string):
    """
    raises:  ValueError
    """
    logger = logging.getLogger('parse_json_request')
    #logger.debug('json_string: ' + json_string)
    
    event = None
    logger.debug('deserializing post data...')
    gen = serializers.deserialize('json', json_string)
    logger.debug('done deserializing')
    try:
        event = gen.next().object
    except Exception, e:
        error_string = 'error deserializing object: ' + str(e)
        logger.info(error_string)
        raise ValueError(error_string)
    return event

def make_bad_request_http_response(error_string):
    return HttpResponse(error_string,mimetype=TEXT_MIME,status=HTTP_BAD_REQUEST)

def extend_int_string(input_string):
    if (len(input_string) == 1):
        return '0' + input_string
    else:
        return input_string


