import unittest,datetime,logging
from event.models import *
from event.utils import *
from tagging.models import *

TESTEVENT_NAME = "testevent"
TESTEVENT_DESCRIPTION = "testdescription"
TESTEVENT_URL = "testurl"
TESTEVENT_ROUTER = "testrouter"
TESTEVENT_IFACE = "testiface"


TESTEVENT_BEGINDATE = datetime.datetime(2008,1,1)
TESTEVENT_ENDDATE = datetime.datetime(2008,1,5)

TESTTAG_NAME = "testtag"

TESTLOG_STRING = 'logging test string'

class EventTestCaseSetup(unittest.TestCase):
    def setUp(self):
        logging.debug("Setting up junit test")
        #Create another object and save it in the test database.
        self.testevent = Event(name=TESTEVENT_NAME,
                         description=TESTEVENT_DESCRIPTION, 
                         begin_time=TESTEVENT_BEGINDATE,
                         end_time=TESTEVENT_ENDDATE,
                         url=TESTEVENT_URL, 
                         router=TESTEVENT_ROUTER,
                         iface=TESTEVENT_IFACE
                         )
        self.testevent.save()
        
        self.testevent.tags=TESTTAG_NAME
        
    def runTest(self):
        #Sanity test
        self.assertTrue(True)
        
    def tearDown(self):
        logging.debug("tearing down junit test")
        self.testevent.delete()
        

class LoggingTestCase(EventTestCaseSetup):
    def runTest(self):
        logging.error(TESTLOG_STRING)
        from settings import LOG_FILENAME
        try:
            f = open(LOG_FILENAME,'r')
            s = 'notempty'
            while (s != ''):
                last = s
                s=f.readline()
            
            if last.find(TESTLOG_STRING) ==-1:
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
        self.assertTrue(len(events.filter(name=TESTEVENT_NAME))==1)
        
        testevent = events.get(name=TESTEVENT_NAME)
        self.assertTrue(testevent.description==TESTEVENT_DESCRIPTION)
        self.assertTrue(testevent.url==TESTEVENT_URL)
        self.assertTrue(testevent.router==TESTEVENT_ROUTER)
        self.assertTrue(testevent.iface==TESTEVENT_IFACE)
        self.assertTrue(testevent.begin_time==TESTEVENT_BEGINDATE)
        self.assertTrue(testevent.end_time==TESTEVENT_ENDDATE)
        
class TagsTestCase(EventTestCaseSetup):
    def runTest(self):
        logging.info( "TagsTestCase: Tags in database: " + str(Tag.objects.all()))
        testtag=Tag.objects.all().get(name=TESTTAG_NAME)
        
        testevents = TaggedItem.objects.get_by_model(Event,testtag)
        
        self.assertTrue(len(testevents)==1)
        self.assertTrue(testevents[0].name==TESTEVENT_NAME)
        
        testevent = Event.objects.all().get(name=TESTEVENT_NAME)
        
        self.assertTrue(len(testevent.tags)==1)
        self.assertTrue(testevent.tags[0]==testtag)