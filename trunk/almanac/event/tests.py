import unittest
import datetime
import logging
from event.models import *
from event.utils import *
from tagging.models import *

EVENT_NAME = "testevent"
EVENT_DESCRIPTION = "testdescription"
EVENT_URL = "testurl"
EVENT_ROUTER = "testrouter"
EVENT_IFACE = "testiface"

EVENT_BEGINDATETIME = datetime.datetime(2008,1,1)
EVENT_ENDDATETIME = datetime.datetime(2008,1,5)

TAG_NAME = "testtag"

LOG_STRING = 'logging test string'

class EventTestCaseSetup(unittest.TestCase):
    def setUp(self):
        logging.debug("Setting up junit test")
        #Create another object and save it in the test database.
        self.test_event = Event(name=EVENT_NAME,
                         description=EVENT_DESCRIPTION, 
                         begin_datetime=EVENT_BEGINDATETIME,
                         end_datetime=EVENT_ENDDATETIME,
                         url=EVENT_URL, 
                         router=EVENT_ROUTER,
                         iface=EVENT_IFACE
                         )
        self.test_event.save()
        
        self.test_event.tags = TAG_NAME
        
    def runTest(self):
        #Sanity test
        self.assertTrue(True)
        
    def tearDown(self):
        logging.debug("tearing down junit test")
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
        events = Event.objects.all()
        
        logging.info( "DatabaseTestCase: Objects in database: " + str(events))
        
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
        logging.info( "TagsTestCase: Tags in database: " + str(Tag.objects.all()))
        test_tag = Tag.objects.all().get(name=TAG_NAME)
        
        test_events = TaggedItem.objects.get_by_model(Event,test_tag)
        
        self.assertTrue(len(test_events) == 1)
        self.assertTrue(test_events[0].name == EVENT_NAME)
        
        test_event = Event.objects.all().get(name=EVENT_NAME)
        
        self.assertTrue(len(test_event.tags) == 1)
        self.assertTrue(test_event.tags[0] == test_tag)