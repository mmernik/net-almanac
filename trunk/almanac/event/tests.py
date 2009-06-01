import unittest,datetime,logging
from event.models import Event

experiment = "experiment"
begin_date = datetime.datetime(2008,1,1)

class EventTestCaseSetup(unittest.TestCase):
    def setUp(self):
        #Create 2 objects and save them in the test database.
        exp = Event(name=experiment,
                         description="a physics experiment", 
                         begin_time=begin_date,
                         end_time=datetime.datetime(2008,1,10))
        exp.save()
        
        upgrade = Event(name="upgrade",
                         description="upgrading infrastructure", 
                         begin_time=datetime.datetime(2008,2,5),
                         end_time=datetime.datetime(2008,2,12))
        upgrade.save()
        
    def runTest(self):
        #Sanity test
        self.assertTrue(True)

class LoggingTestCase(EventTestCaseSetup):
    def runTest(self):
        print "There should be 4 logging messages after this message"
        logging.debug('this is a debug message')
        logging.info('this is an info message')
        logging.warn('this is a warning message')
        logging.error('this is an error message')
        
class DatabaseTestCase(EventTestCaseSetup):
    def runTest(self):
        print "Objects in database: " + str(Event.objects.all())
        self.assertTrue(len(Event.objects.all())==2)
        self.assertTrue(Event.objects.all()[0].name==experiment)
        self.assertTrue(Event.objects.all()[0].begin_time==begin_date)
        