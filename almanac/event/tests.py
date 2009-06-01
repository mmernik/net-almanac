import unittest,datetime,logging
from event.models import Event

class EventTestCase(unittest.TestCase):
    def setUp(self):
        self.exp = Event(name="experiment",
                         description="a physics experiment", 
                         begin_time=datetime.date(2008,1,1),
                         end_time=datetime.date(2008,1,10))
        self.exp.save()
        
    def runTest(self):
        print "sanity test Running"
        self.assertTrue(True)
        