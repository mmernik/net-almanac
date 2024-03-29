import unittest
import datetime
import logging
import urllib2
import os
import time

from django.test.client import Client
import net_almanac.views
from net_almanac.models import Event, EventForm, MAX_LENGTH_FIELD, MAX_LENGTH_DESCRIPTION, MAX_LENGTH_TAGS
from net_almanac.testdata import bad_json_strings, NEW_DESCRIPTION, good_json_string, bad_create_string, good_create_strings, json_headers
from tagging.models import *

import twill
from twill import commands as tc
from twill.shell import TwillCommandLoop
from django.test import TestCase
from django.core import serializers
from django.core.servers.basehttp import AdminMediaHandler
from django.core.handlers.wsgi import WSGIHandler
from StringIO import StringIO

import wsgi_intercept.httplib2_intercept
wsgi_intercept.httplib2_intercept.install()
import wsgi_intercept
import httplib2

import almanac.api

EVENT_NAME = "testevent"
EVENT_DESCRIPTION = "testdescription"
EVENT_URL = "testurl"

EVENT_BEGINDATETIME = datetime.datetime(2008,1,1)
EVENT_ENDDATETIME = datetime.datetime(2008,1,5)


TAG_NAME_1 = 'testtag1'
TAG_NAME_2 = 'testtag2'
TAG_STRING = TAG_NAME_1 + ' ' + TAG_NAME_2

LOG_STRING = 'logging test string'

HTML_MIME = 'text/html'
TEXT_MIME = 'text/plain'
JSON_MIME = 'application/json'

HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_NOT_IMPLEMENTED = 501
HTTP_OK = 200

TEST_PORT = 47630 #some random port I picked

URL_BASE = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/'


class EventTestCaseSetup(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger('EventTestCaseSetup')
        logger.debug("setting up junit test")
        #Create another object and save it in the test database.
        self.test_event = Event(name=EVENT_NAME,
                         description=EVENT_DESCRIPTION, 
                         begin_datetime=EVENT_BEGINDATETIME,
                         end_datetime=EVENT_ENDDATETIME,
                         url=EVENT_URL, 
                         tags=TAG_STRING
                         )
        self.test_event.save()
        
        
        
    def tearDown(self):
        logger = logging.getLogger('EventTestCaseSetup')
        logger.debug("tearing down junit test")
        self.test_event.delete()
      

class LoggingTestCase(EventTestCaseSetup):
    def runTest(self):
        #Log an error and then make sure it's there.
        logging.error(LOG_STRING)
        from settings import LOG_FILENAME
        try:
            f = open(LOG_FILENAME,'r')
            s = 'notempty'
            while (s != ''):
                last = s
                s = f.readline()
            
            if last.find(LOG_STRING) == -1:
                self.assertTrue(False)
        except IOError:
            self.assertTrue(False)
        finally:
            f.close()
        
class DatabaseTestCase(EventTestCaseSetup):
    def runTest(self):
        logger = logging.getLogger('DatabaseTestCase')
        events = Event.objects.all()
        
        logger.info( "Objects in database: " + str(events))
        
        #check if all data is the same as assigned.
        self.assertTrue(len(events.filter(name = EVENT_NAME))==1)
        
        testevent = events.get(name = EVENT_NAME)
        self.assertTrue(testevent.description == EVENT_DESCRIPTION)
        self.assertTrue(testevent.url == EVENT_URL)
        self.assertTrue(testevent.begin_datetime == EVENT_BEGINDATETIME)
        self.assertTrue(testevent.end_datetime == EVENT_ENDDATETIME)
        
class TagsTestCase(EventTestCaseSetup):
    def runTest(self):
        logger = logging.getLogger('TagsTestCase')
        logger.info( "Tags in database: " + str(Tag.objects.all()))
        test_tag = Tag.objects.all().get(name=TAG_NAME_1)
        
        test_events = TaggedItem.objects.get_by_model(Event,test_tag)
        
        self.assertTrue(len(test_events) == 1)
        self.assertTrue(test_events[0].name == EVENT_NAME)
        
        test_event = Event.objects.all().get(name=EVENT_NAME)
        
        self.assertTrue(len(Tag.objects.get_for_object(test_event)) == 2)
        self.assertTrue(test_event.tags == TAG_STRING)
        
class HTMLResponseTestCase(EventTestCaseSetup):
    def runTest(self):
        #some sanity HTML tests using the provided test client
        c = Client()
        response = c.get('/net_almanac/event/')
        self.assertTrue(response.status_code == HTTP_OK)
        self.assertTrue(response.has_header('content-type'))
        self.assertTrue(response._headers['content-type'][1].find(HTML_MIME) != -1)
        self.assertTrue(response.content.find('html') != -1)
        

class TestWSGI(unittest.TestCase):
    """
    We use WSGI intercept so that we can hook it up to httplib2, a library that
    supports PUT and DELETE http requests.  Most REST API tests use WSGI.
    """
    def setUp(self):
        app = AdminMediaHandler(WSGIHandler())
        wsgi_intercept.add_wsgi_intercept('127.0.0.1', TEST_PORT, lambda: app)

    def tearDown(self):
        wsgi_intercept.remove_wsgi_intercept()
        
class TestDelete(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestDelete")
        url = URL_BASE + '3/'
        
        h = httplib2.Http()
        
        logger.info('accessing with DELETE: ' + url)
        response, content = h.request(url,'DELETE', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_NOT_FOUND)


class TestPut(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestPut")
        h = httplib2.Http()
        url = URL_BASE + '1/'
        
        for input in bad_json_strings:
            logger.info('accessing: ' + url)
            response, content = h.request(url, 'PUT', input, headers=json_headers)
            
            self.assertTrue(response.status == HTTP_BAD_REQUEST)
            logger.info('got expected error message: ' + content)
            
        logger.info('get current description')
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        get_event = serializers.deserialize('json',content).next().object
        self.assertTrue(get_event.description != NEW_DESCRIPTION)
        
        logger.info('putting new description in place')
        response, content = h.request(url, 'PUT', good_json_string, headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        
        logger.info('checking for new description')
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        get_event = serializers.deserialize('json',content).next().object
        self.assertTrue(get_event.description == NEW_DESCRIPTION)

class Test404(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI Test404")
        h = httplib2.Http()
        url = URL_BASE + '8/'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_NOT_FOUND)
        
class TestPost(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestPost")
        h = httplib2.Http()
        
        url = URL_BASE
        logger.info('accessing with POST with bad string: ' + url)
        response, content = h.request(url,'POST', bad_create_string, headers=json_headers)
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        logger.info('got expected error message: ' + content)
        
        logger.info('accessing with POST with good string: ' + url)
        response, content = h.request(url,'POST', good_create_strings[0], headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        
        #The 'good' string is now bad since there is now an object with that ID
        logger.info('accessing with POST with bad string: ' + url)
        response, content = h.request(url,'POST', good_create_strings[0], headers=json_headers) 
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        logger.info('got expected error message: ' + content)
        
        #The second good string has a null id, so we should be able to create it twice.
        logger.info('accessing with POST with good string: ' + url)
        response, content = h.request(url,'POST', good_create_strings[1], headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
            
        logger.info('accessing with POST with good string: ' + url)
        response, content = h.request(url,'POST', good_create_strings[1], headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)

        
class TestTags(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestTags")
        h = httplib2.Http()
        
        #test one tag
        url = URL_BASE + '?tag=esnet'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') > 1)
        
        #test two tags
        url = URL_BASE + '?tag=esnet&tag=lbnl'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        #there is only one event in initial data with both these tags
        self.assertTrue(content.count('"description"') == 1) 
        
        #test an unknown tag
        url = URL_BASE + '?tag=g484848a' #silly name
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 0)
        

class TestDate(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestDate")
        h = httplib2.Http()
        
        url = URL_BASE + '?date=2009-01-15'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 2)

        url = URL_BASE + '?date=2009-01-16'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 1)
        
        #malformed date but dateutil deals with it
        url = URL_BASE + '?date=2009-01-15a'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        
        #bad date
        url = URL_BASE + '?date=2009-01-s5'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        self.assertTrue(response['content-type'] == TEXT_MIME)
        
        #another bad date
        url = URL_BASE + '?date=2009-02-30'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        self.assertTrue(response['content-type'] == TEXT_MIME)
        
        #use begin//end dates
        url = URL_BASE + '?begin_date=2009-01-01&end_date=2009-01-30'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 2)
        
        #no begin date: end date is ignored.
        url = URL_BASE + '?end_date=2009-01-30'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') > 2)

class TestTimelineData(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestDate")
        h = httplib2.Http()
        
        url = URL_BASE + 'timeline/data/'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET')
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"iso8601"') == 1)

class TestTextSearch(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestDate")
        h = httplib2.Http()
        
        #empty search should be ignored
        url = URL_BASE + '?name='
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') > 2)
        
        url = URL_BASE + '?name=experiment'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 1)
        
        url = URL_BASE + '?description=lorem'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 2)
        
        url = URL_BASE + '?search=http://www.es.net'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 1)
        

def twill_quiet():
    twill.set_output(StringIO())
    
class TwillTestCaseSetup(unittest.TestCase):
    def setUp(self):
        app = AdminMediaHandler(WSGIHandler())
        twill.add_wsgi_intercept('127.0.0.1', TEST_PORT, lambda: app)
    
    def twill_teardown(self):
        twill.remove_wsgi_intercept('127.0.0.1', TEST_PORT)

class TwillTestCase(TwillTestCaseSetup):
    def runTest(self):
        """
        The twill test case is useful for emulating a user using HTML forms and clicking on buttons.
        Note we cannot connect to the twill server using urllib2 or any other third party client.
        Also, we cannot verify the header content in a twill response.
        """
        FILTER_FORM = 2
        
        logger = logging.getLogger("TwillTestCase")
        url = URL_BASE
        twill_quiet()
        logger.info('accessing ' + url)
        tc.go(url)
        tc.find("html") # sanity check that this is a html request.
        
        url = URL_BASE + 'filter/'
        logger.info('accessing ' + url)
        tc.go(url)
        tc.formvalue(FILTER_FORM,'tag','esnet')
        tc.submit(9) #simulates a click on the "create filter" button
        tc.find("html")
        tc.find('<table class="sortable">') #a line in event.list.html
        tc.notfind('experiment') #should be filtered out
        
        tc.go(url)
        tc.formvalue(FILTER_FORM,'display','timeline')
        tc.submit(9) #click should direct us to timeline.
        tc.find("html")
        tc.notfind('<table class="sortable">') 
        
        tc.go(url)
        tc.formvalue(FILTER_FORM,'display','json')
        tc.submit(9) #click should give us JSON object.
        tc.find('"pk": 1') #part of JSON string.
        tc.notfind("html")
        
        tc.go(url)
        tc.formvalue(FILTER_FORM,'name','upgrade')
        tc.formvalue(FILTER_FORM,'search','www.es.net')
        tc.formvalue(FILTER_FORM,'description','infrastructure')
        tc.submit(9)
        tc.find('html')
        tc.find('www.es.net') #part of the upgrade event.
        
        #Set headers to contain only the json mime
        tc.clear_extra_headers()
        tc.add_extra_header('Accept',JSON_MIME)
        
        url = URL_BASE
        logger.info('accessing ' + url)
        tc.go(url)
        logger.debug('JSON data:' + tc.show())
        tc.notfind("html") 
        tc.find('"name": "experiment"') #data from the fixture formatted by default serializer
        tc.find('"tags": "esnet"')
        
        url = URL_BASE + '1/'
        logger.info('accessing ' + url)
        tc.go(url)
        tc.notfind("html")
        tc.find('"name": "experiment"') 
        tc.notfind('"tags": "esnet"') 
        
class TestAPI(TestWSGI):
    def runTest(self):
        #check if some constants are the same.
        self.assertTrue(almanac.api.MAX_LENGTH_FIELD == MAX_LENGTH_FIELD)
        self.assertTrue(almanac.api.MAX_LENGTH_DESCRIPTION == MAX_LENGTH_DESCRIPTION)
        self.assertTrue(almanac.api.MAX_LENGTH_TAGS == MAX_LENGTH_TAGS)
        self.assertTrue(almanac.api.FORBIDDEN_CHARS == net_almanac.views.FORBIDDEN_CHARS)
        
        almanac = almanac.api.NetAlmanac(URL_BASE)
        
        #test get all events
        api_events = almanac.get_all_events()
        self.assertTrue(len(api_events)>2)
        for api_event in api_events:
            self.assertTrue(almanac.api.validate_event(api_event))
        
        #test get single event    
        self.assertTrue(almanac.get_event(1).name == "experiment")
        self.assertTrue(almanac.get_event(200) == None)
        
        #test filtering
        filtered = almanac.get_filtered_events(name="experiment")
        self.assertTrue(len(filtered)==1)
        filtered = almanac.get_filtered_events(tags=["esnet","january"])
        self.assertTrue(len(filtered)==2)  
        filtered = almanac.get_filtered_events(search="www.es.net", description="upgrading infrastructure")
        self.assertTrue(len(filtered)==1)
        filtered = almanac.get_filtered_events(tags=["notag","faketag"])
        self.assertTrue(len(filtered)==0)
        
        #test saves
        event = almanac.get_filtered_events(name="experiment")[0]
        self.assertTrue(event.url=="http://www.lbl.gov")
        event.url = "http://www.es.net"
        almanac.save_event(event)
        event = almanac.get_filtered_events(name="experiment")[0]
        self.assertTrue(event.url=="http://www.es.net")
        event.url = "http://www.lbl.gov"
        almanac.save_event(event)
        event = almanac.get_filtered_events(name="experiment")[0]
        self.assertTrue(event.url=="http://www.lbl.gov")
        
        event.name = ""
        try:
            #Try to save a bad event and induce a specific error message
            almanac.save_event(event)
            self.assertTrue(False)
        except ValueError, e:
            if str(e).count("'name' property cannot be empty") == 0:
                self.assertTrue(False)
        
        #test create_event
        to_create = almanac.api.Event(20,
                                          'api_created',
                                          'description',
                                          datetime.datetime(2009,2,2),
                                          datetime.datetime(2009,2,3),
                                          'url',
                                          ['tags','anothertag'])
        almanac.create_event(to_create)
        event = almanac.get_filtered_events(name="api_created")[0]
        self.assertTrue(event.description == 'description')
        
        #induce a id number collision.
        to_create.id=1
        try:
            almanac.create_event(to_create)
            self.assertTrue(False)
        except ValueError, e:
            if str(e).count("id is already taken by another event") == 0:
                self.assertTrue(False)
        
        #test deletes
        to_create.id=20
        almanac.delete_event(to_create)
        filtered = almanac.get_filtered_events(name="api_created")
        self.assertTrue(len(filtered) == 0)
        try:
            almanac.delete_event(to_create)
            self.assertTrue(False)
        except ValueError, e:
            self.assertTrue(str(e).index('404') != -1)
