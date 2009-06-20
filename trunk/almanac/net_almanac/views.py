from django.http import Http404
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404

from almanac.net_almanac.models import *
from tagging.models import *

import logging
import datetime
import dateutil.parser
import tagging

JSON_MIME = 'application/json'
TEXT_MIME = 'text/plain'

HTTP_BAD_REQUEST = 400
HTTP_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501

HTTPRESPONSE_NOT_IMPLEMENTED = HttpResponse('request type not supported at this URL',
                                            mimetype=TEXT_MIME,
                                            status=HTTP_NOT_IMPLEMENTED)

ONE_DAY = datetime.timedelta(1)

INVALID_ERROR_STRING = "Submitted form is not valid"

def root(request):
    #for now, just a redirect
    return HttpResponseRedirect('/net_almanac/event/')

def tag(request,tag_name):
    #filters objects by tags, then returns.  Only supports GET
    logger = logging.getLogger('view tag')
    logger.debug('hit')
    tag = Tag.objects.get(name=tag_name)
    events = TaggedItem.objects.get_by_model(Event,tag)
    if is_json_request(request):
        json_data = serializers.serialize('json',events)
        return HttpResponse(json_data,mimetype=JSON_MIME)
    else:
        return render_to_response('net_almanac/tag_detail.html',
                                  {'tag':tag,
                                   'event_list':events})

def tag_list(request):
    #only supports GET.  Orders tags by the most common
    logger = logging.getLogger('view tag_list')
    logger.debug('hit')
    tags_list = get_all_tags_with_frequency()
    tags_list.sort(tag_compare)
    return render_to_response('net_almanac/tag_list.html',
                              {'tag_list':tags_list,})
    
def tag_clean(request):
    #deletes all unused tags
    if request.method == 'POST':
        for tag in Tag.objects.all():
            if get_tag_frequency(tag) == 0:
                tag.delete()
        return HttpResponseRedirect('/net_almanac/event/tag/')
    else:
        return HTTPRESPONSE_NOT_IMPLEMENTED

def list_events(request):
    logger = logging.getLogger('view list_events')
    
    logger.info('hit')
    
    events = Event.objects.all()
    
    #These variables are used to customize the rendered HTML
    is_custom_request = False
    tags_list = None
    date = None
    begin_date = None
    end_date = None
    
    #filter the events if we are a GET request.
    if request.method=='GET':
        get_data = request.GET
        logger.debug('get parameters: ' + str(get_data))
        #filter by tags
        tags_list = get_data.getlist('tag')
        if tags_list:
            logger.info('tags_list: ' + str(tags_list))
            is_custom_request = True
            events = TaggedItem.objects.get_by_model(Event, tags_list)
            logger.info("filtered by tags: " + str(events))
        
        if get_data.has_key('date') and not is_empty_or_space(get_data['date']):
            is_custom_request = True
            #filter by all events that fall on this date
            date = get_data['date']
            logger.info('filtering by date: ' + date)
            try:
                #try parsing the date.
                dateutil.parser.parse(date)
            except ValueError, e:
                logger.info('error parsing date: ' + str(e))
                return make_bad_request_http_response(str(e))
            
            events = events.filter(begin_datetime__lte=increment_day(date))
            events = events.filter(end_datetime__gte=current_day(date))
            
        elif (get_data.has_key('begin_date') 
              and get_data.has_key('end_date')
              and not is_empty_or_space(get_data['begin_date'])
              and not is_empty_or_space(get_data['end_date'])):
            is_custom_request = True
            logger.info('has begin and end date')
            begin_date = get_data['begin_date']
            end_date = get_data['end_date']
            try:
                #try parsing the dates.
                dateutil.parser.parse(begin_date)
                dateutil.parser.parse(end_date)
            except ValueError, e:
                logger.info('error parsing dates: ' + str(e))
                return make_bad_request_http_response(str(e))
            events = events.filter(begin_datetime__lte=increment_day(end_date))
            events = events.filter(end_datetime__gte=current_day(begin_date))
    
    if is_json_request(request):
        #return serialized objects.
        logger.debug('json request')
        if request.method == 'GET':
            json_data = serializers.serialize('json',events)
            return HttpResponse(json_data,mimetype=JSON_MIME)
        elif request.method == 'POST':
            logger.debug('request to POST new event object')
            
            deserialized_event = None
            try:
                logger.debug('parsing json')
                deserialized_event = parse_json_request(request.raw_post_data)
                
                validate_event(deserialized_event) #raises ValueError
                
                filtered_list = Event.objects.filter(id=deserialized_event.id)
                if (filtered_list):
                    logger.debug('deserialized_event.id: ' + str(deserialized_event.id))
                    logger.debug('other event: ' + str(filtered_list))
                    assert len(filtered_list) == 1
                    error_str = 'id is already taken by another event'
                    logger.info(error_str)
                    return make_bad_request_http_response(error_str)
                logger.debug('trying to save new event...')
                deserialized_event.save()
                logger.info('event saved!')
                
            except ValueError, e:
                #bad format
                logger.info('ValueError: ' + str(e))
                return make_bad_request_http_response(str(e))
            except Exception, e:
                logger.error('unexpected exception encountered: ' + str(e))
                return HttpResponse('unexpected exception encountered: ' + str(e),
                                    status=HTTP_SERVER_ERROR)
            
            return HttpResponse('new event successfully saved',
                                mimetype=TEXT_MIME)
        else:
            return HTTPRESPONSE_NOT_IMPLEMENTED
        
    else:
        if request.method != 'GET':
            return HTTPRESPONSE_NOT_IMPLEMENTED
        
        tags_string = ""
        if tags_list:
            tags_string = "with tags '" + "', '".join(tags_list) + "'"
        
        date_string = ""
        if date:
            date_string = "on " + date
        elif begin_date:
            date_string = "between " + begin_date + " and " + end_date
        
        return render_to_response('net_almanac/event_list.html',
                                  {'event_list':events,
                                   'is_custom_request':is_custom_request,
                                   'tags_string':tags_string,
                                   'date_string':date_string,
                                   })

def create_event(request):
    #a GET request returns a new form, and a POST request attempts to create a new event
    logger = logging.getLogger('view create_event')
    
    logger.info('hit')
    logger.debug('request.method='+request.method)
    form = EventForm()
    
    if request.method == 'GET':
        return render_to_response('net_almanac/event_create.html',
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
                logger.debug(INVALID_ERROR_STRING)
                raise ValueError(INVALID_ERROR_STRING)
            
            begin_datetime_string = post_data['begin_date'] + ' ' + post_data['begin_time']
            end_datetime_string = post_data['end_date'] + ' ' + post_data['end_time']
            
            new_event = Event(name=post_data['name'],
                              description=post_data['description'],
                              begin_datetime=dateutil.parser.parse(begin_datetime_string),
                              end_datetime=dateutil.parser.parse(end_datetime_string),
                              url=post_data['url'],
                              router=post_data['router'],
                              iface=post_data['iface'],
                              tags = post_data['tags'])
            
            validate_event(new_event) #raises ValueError
            
            logger.debug('trying to save new event...')
            new_event.save()
            logger.info('save successful! event added: ' + new_event.name)
            
            return HttpResponseRedirect('/net_almanac/event/' + str(new_event.id) + '/')
        
        except ValueError, e:
            logger.info(str(e))
            return render_to_response('net_almanac/event_create.html',
                                      {'form':form,
                                       'form_table':form.as_table(),
                                       'error':str(e)})
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
        return render_to_response('net_almanac/event_update.html',
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
                logger.debug(INVALID_ERROR_STRING)
                raise ValueError(INVALID_ERROR_STRING)
            
            
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
            
            return HttpResponseRedirect('/net_almanac/event/' + str(event.id) + '/')
        
        
        except ValueError, e:
            #TODO: include old user input
            logger.info('bad user input')
            return render_to_response('net_almanac/event_update.html',
                                      {'event': event,
                                       'form':form,
                                       'form_table':form.as_table(),
                                       'error':str(e)})     
        else:
            logger.error('unexpected error!')
        
def delete_event(request,object_id):
    #a GET request gives a confirmation page, and a POST request deletes and redirects
    logger = logging.getLogger('view delete_event')
    
    logger.info('hit')
    logger.debug('request.method='+request.method)
    
    event = get_event_by_id(object_id)
    
    if request.method == 'GET':
        
        return render_to_response('net_almanac/event_confirm_delete.html',
                                  {'event':event,})
        
    elif request.method == 'POST':
        logger.debug('deleting event: ' + event.name)
        
        #we need to delete tags because they are not automatically deleted with delete()
        event.tags = ""
        event.delete()
        logger.info('delete successful! event delete: ' + event.name)
        
        return HttpResponseRedirect('/net_almanac/event/')

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
                return HttpResponse('unexpected exception encountered: ' + str(e), status=HTTP_SERVER_ERROR)
            return HttpResponse('event updated',mimetype=TEXT_MIME)

        elif (request.method == 'DELETE'):
            logger.info('got DELETE request...deleting selected event: ' + event.name)      
            event.delete()
            return HttpResponse('event deleted',mimetype=TEXT_MIME) 
   
        elif (request.method =='POST'):
            #not implemented
            logger.debug('got POST request...dropping')
            return HttpResponse('POST not supported at this URL',
                                mimetype=TEXT_MIME,
                                status=HTTP_NOT_IMPLEMENTED) 

    
    else:
        return render_to_response('net_almanac/event_detail.html',
                                  {'event':event,
                                   'tags':Tag.objects.get_for_object(event)})
        

def filter(request):
    logger = logging.getLogger('view filter')
    logger.info('hit')
    return render_to_response('net_almanac/create_filter.html',
                              {'tag_list':Tag.objects.all()})


def view_by_year(request,year):
    logger = logging.getLogger('view view_by_year')
    logger.info('hit')
    year_int = int(year)
    event_list = Event.objects.filter(begin_datetime__year=year)
    logger.debug('event_list: ' + str(event_list))
    return render_to_response('net_almanac/event_by_year.html',
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
        next_month = '%04d/%02d' % (year_int, month_int+1)
        
    if (month_int==1):
        last_month = str(year_int-1) + '/12'
    else:
        last_month = '%04d/%02d' % (year_int, month_int-1)
        
        
    event_list = Event.objects.filter(begin_datetime__year=year_int,
                                      begin_datetime__month=month_int)
    
    month_str = datetime.date(2000, month_int, 1).strftime('%B')
    
    return render_to_response('net_almanac/event_by_month.html',
                              {'event_list':event_list,
                               'year':year,
                               'month':month,
                               'next_month':next_month,
                               'last_month':last_month,
                               'next_year':year_int+1,
                               'last_year':year_int-1,
                               'month_str':month_str
                               })
        
def view_by_date(request):
    #default date view, direct to all events this year.
    return HttpResponseRedirect('/net_almanac/event/date/' + str(datetime.date.today().year) + '/')

def validate_event(event):
    """
    Always call this before saving an event!
    
    raises ValueError when there is some inconsistency
    """
    logger = logging.getLogger('validate_event')
    
    
    if (event.__class__ != Event):
        logger.info('Object is not of type Event')
        raise ValueError('Object is not of type Event')
    
    logger.debug('checking event with name: ' + event.name)
    
    if is_empty_or_space(event.name):
        raise ValueError("'name' property cannot be empty.")
    if is_empty_or_space(event.description):
        raise ValueError("'description' property cannot be empty.")
    
    logger.debug('parsing tags')
    for tag in tagging.utils.parse_tag_input(event.tags):
        #normally commas are delimiters, but if they are between double-quotes they become tags
        if not tag.isalnum():
            raise ValueError('Tags must be alphanumeric [a-z][A-Z][0-9].')
        
    event.tags = format_tag_string(event.tags)
    
    logger.debug('checking datetime')
    if event.end_datetime < event.begin_datetime:
        raise ValueError('The end date cannot be before the begin date.')
    
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
    Takes in some user-inputted tag string and formats it into a pretty string.
    """
    logger = logging.getLogger('format_tag_string')
    return ' '.join(tagging.utils.parse_tag_input(tags_string))


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

def tag_compare(tag1, tag2):
    if tag1.frequency > tag2.frequency:
        return -1
    elif tag1.frequency == tag2.frequency:
        return 0
    else:
        return 1
    
def get_all_tags_with_frequency():
    to_return = []
    for tag in Tag.objects.iterator():
        tag.frequency = get_tag_frequency(tag)
        to_return.append(tag)
    return to_return

def get_tag_frequency(tag):
    return len(TaggedItem.objects.get_by_model(Event,tag))

def increment_day(date_string):
    d = dateutil.parser.parse(date_string)
    d = d + ONE_DAY
    return d.strftime('%Y-%m-%d')

#fixes some input errors
def current_day(date_string):
    return dateutil.parser.parse(date_string).strftime('%Y-%m-%d')
    