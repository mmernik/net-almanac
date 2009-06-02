import unittest,datetime,logging
from event.models import *
from event.utils import *

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
        
        self.testtag = Tag(name=TESTTAG_NAME)
        self.testtag.save()
        
        self.ta = TagAssignment(tag=self.testtag,event=self.testevent)
        self.ta.save()
        
    def runTest(self):
        #Sanity test
        self.assertTrue(True)
        
    def tearDown(self):
        logging.debug("tearing down junit test")
        self.ta.delete()
        self.testevent.delete()
        self.testtag.delete()
        

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
        logging.info( "DatabaseTestCase: Objects in database: " + str(Event.objects.all()))
        self.assertTrue(len(Event.objects.all())==4)
        
        #check if all data is the same as assigned.
        testevent = Event.objects.all().get(name=TESTEVENT_NAME)
        self.assertTrue(testevent.description==TESTEVENT_DESCRIPTION)
        self.assertTrue(testevent.url==TESTEVENT_URL)
        self.assertTrue(testevent.router==TESTEVENT_ROUTER)
        self.assertTrue(testevent.iface==TESTEVENT_IFACE)
        self.assertTrue(testevent.begin_time==TESTEVENT_BEGINDATE)
        self.assertTrue(testevent.end_time==TESTEVENT_ENDDATE)
        
class TagsTestCase(EventTestCaseSetup):
    def runTest(self):
        testtag=Tag.objects.all().get(name=TESTTAG_NAME)
        ta = TagAssignment.objects.all().get(tag=testtag)
        self.assertTrue(ta.event.name==TESTEVENT_NAME)
        
class UtilsTestCase(EventTestCaseSetup):
    def runTest(self):
        self.assertTrue(len(getEvents(Tag.objects.all().get(name=TESTTAG_NAME))) == 1)
        self.assertTrue(len(getTags(Event.objects.all().get(name=TESTEVENT_NAME))) == 1)