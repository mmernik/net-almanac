import unittest
import datetime
import logging
import urllib2
import os
import time

from django.test.client import Client
from event.models import *
from event.utils import *
from tagging.models import *

import twill
from twill import commands as tc
from twill.shell import TwillCommandLoop
from django.test import TestCase
from django.core.servers.basehttp import AdminMediaHandler
from django.core.handlers.wsgi import WSGIHandler
from StringIO import StringIO


EVENT_NAME = "testevent"
EVENT_DESCRIPTION = "testdescription"
EVENT_URL = "testurl"
EVENT_ROUTER = "testrouter"
EVENT_IFACE = "testiface"

EVENT_BEGINDATETIME = datetime.datetime(2008,1,1)
EVENT_ENDDATETIME = datetime.datetime(2008,1,5)


TAG_NAME_1 = 'testtag1'
TAG_NAME_2 = 'testtag2'
TAG_STRING = TAG_NAME_1 + ', ' + TAG_NAME_2

LOG_STRING = 'logging test string'

HTML_MIME = 'text/html'
JSON_MIME = 'application/json'

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
        response = c.get('/event/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.has_header('content-type'))
        self.assertTrue(response._headers['content-type'][1].find(HTML_MIME) != -1)
        self.assertTrue(response.content.find('<html>') != -1)
        


def twill_setup():
    app = AdminMediaHandler(WSGIHandler())
    twill.add_wsgi_intercept('127.0.0.1', TEST_PORT, lambda: app)

def twill_teardown():
    twill.remove_wsgi_intercept('127.0.0.1', TEST_PORT)


def twill_quiet():
    twill.set_output(StringIO())


class TwillTestCaseSetup(unittest.TestCase):
    def setUp(self):
        twill_setup()
    
    def twill_teardown(self):
        twill_teardown()

class JSONTestCase(TwillTestCaseSetup):
    def runTest(self):
        """
        Note we cannot connect to the twill server using urllib2 or any other third party client.
        Also, we cannot verify the header content in a twill response.
        """
        
        logger = logging.getLogger("JSONTestCase")
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/event/'
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
        
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/event/1/'
        logger.info('accessing ' + url)
        tc.go(url)
        tc.notfind("html")
        tc.find('"name": "experiment"') 
        tc.notfind('"tags": "esnet"') 
        
        
class JSONPOSTTestCase(TwillTestCaseSetup):
    def runTesT(self):
        logger = logging.getLogger("JSONPOSTTestCase")
        from testdata import bad_json_strings, good_json_string
        url = 'http://127.0.0.1:' + str(TEST_PORT) + '/event/1/update/'
        tc.clear_extra_headers()
        tc.add_extra_header('Accept',JSON_MIME)
        
        logger.info('accessing ' + url)
        tc.go(url)
        tc.code(501) #not implemented
        #actual edit not yet implemented: twill doesn't support
        
        
        
        
        
