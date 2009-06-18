import unittest
import datetime
import logging
import urllib2
import os
import time

from django.test.client import Client
from net_almanac.models import *
from net_almanac.testdata import bad_json_strings, NEW_DESCRIPTION, good_json_string, bad_create_string, good_create_string, json_headers
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

EVENT_NAME = "testevent"
EVENT_DESCRIPTION = "testdescription"
EVENT_URL = "testurl"
EVENT_ROUTER = "testrouter"
EVENT_IFACE = "testiface"

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
                         router=EVENT_ROUTER,
                         iface=EVENT_IFACE,
                         tags=TAG_STRING
                         )
        self.test_event.save()
        
        
        
    def tearDown(self):
        logger = logging.getLogger('EventTestCaseSetup')
        logger.debug("tearing down junit test")
        self.test_event.delete()
      

class LoggingTestCase(EventTestCaseSetup):
    def runTest(self):
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
        self.assertTrue(testevent.router == EVENT_ROUTER)
        self.assertTrue(testevent.iface == EVENT_IFACE)
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
        #some sanity HTML tests not using twill but the provided test client
        c = Client()
        response = c.get('/net_almanac/event/')
        self.assertTrue(response.status_code == HTTP_OK)
        self.assertTrue(response.has_header('content-type'))
        self.assertTrue(response._headers['content-type'][1].find(HTML_MIME) != -1)
        self.assertTrue(response.content.find('html') != -1)
        

class TestWSGI(unittest.TestCase):
    def setUp(self):
        app = AdminMediaHandler(WSGIHandler())
        wsgi_intercept.add_wsgi_intercept('127.0.0.1', TEST_PORT, lambda: app)

    def tearDown(self):
        wsgi_intercept.remove_wsgi_intercept()
        
class TestDelete(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestDelete")
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/3/'
        
        h = httplib2.Http()
        
        events = Event.objects.all()
        
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
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/1/'
        
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
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/8/'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_NOT_FOUND)
        
class TestPost(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestPost")
        h = httplib2.Http()
        
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/'
        logger.info('accessing with POST with bad string: ' + url)
        response, content = h.request(url,'POST', bad_create_string, headers=json_headers)
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        logger.info('got expected error message: ' + content)
        
        logger.info('accessing with POST with good string: ' + url)
        response, content = h.request(url,'POST', good_create_string, headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        
        #The 'good' string is now bad since there is now an object with that ID
        logger.info('accessing with POST with bad string: ' + url)
        response, content = h.request(url,'POST', good_create_string, headers=json_headers) 
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        logger.info('got expected error message: ' + content)

        
class TestTags(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestTags")
        h = httplib2.Http()
        
        #test one tag
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?tag=esnet'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') > 1)
        
        #test two tags
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?tag=esnet&tag=lbnl'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        #there is only one event in initial data with both these tags
        self.assertTrue(content.count('"description"') == 1) 
        
        #test an unknown tag
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?tag=g484848a' #silly name
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 0)
        

class TestDate(TestWSGI):
    def runTest(self):
        logger = logging.getLogger("TestWSGI TestDate")
        h = httplib2.Http()
        
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?date=2000-01-15'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 2)

        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?date=2000-01-16'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        self.assertTrue(content.count('"description"') == 1)
        
        #malformed date but dateutil deals with it
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?date=2000-01-15a'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_OK)
        self.assertTrue(response['content-type'] == JSON_MIME)
        
        #really bad date
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?date=2000-01-s5'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        self.assertTrue(response['content-type'] == TEXT_MIME)
        
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/?date=2000-02-30'
        logger.info('accessing with GET: ' + url)
        response, content = h.request(url,'GET', headers=json_headers)
        self.assertTrue(response.status == HTTP_BAD_REQUEST)
        self.assertTrue(response['content-type'] == TEXT_MIME)

def twill_quiet():
    twill.set_output(StringIO())
    
class TwillTestCaseSetup(unittest.TestCase):
    def setUp(self):
        app = AdminMediaHandler(WSGIHandler())
        twill.add_wsgi_intercept('127.0.0.1', TEST_PORT, lambda: app)
    
    def twill_teardown(self):
        twill.remove_wsgi_intercept('127.0.0.1', TEST_PORT)

class JSONTestCase(TwillTestCaseSetup):
    def runTest(self):
        """
        Note we cannot connect to the twill server using urllib2 or any other third party client.
        Also, we cannot verify the header content in a twill response.
        """
        
        logger = logging.getLogger("JSONTestCase")
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/'
        twill_quiet()
        logger.info('accessing ' + url)
        tc.go(url)
        tc.find("html") # sanity check that this is a html request.
        
        tc.clear_extra_headers()
        tc.add_extra_header('Accept',JSON_MIME)
        
        logger.info('accessing ' + url)
        tc.go(url)
        logger.debug('JSON data:' + tc.show())
        tc.notfind("html") 
        tc.find('"name": "experiment"') #data from the fixture formatted by default serializer
        tc.find('"tags": "esnet"')
        
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/net_almanac/event/1/'
        logger.info('accessing ' + url)
        tc.go(url)
        tc.notfind("html")
        tc.find('"name": "experiment"') 
        tc.notfind('"tags": "esnet"') 
        
