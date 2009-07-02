import datetime
import httplib2
import simplejson
import dateutil.parser

"""
A python interface to almanac's REST requests.
"""


HTTP_OK = 200
JSON_HEADERS = {'accept':'application/json'}


MAX_LENGTH_FIELD = 100
MAX_LENGTH_DESCRIPTION = 500


class Event():
    
    """
    An event represents one event object in the almanac database.
    See README.txt for more information.
    """
    
    def __init__(self,
             id,
             name,
             description,
             begin_datetime,
             end_datetime,
             url,
             iface,
             router,
             tags,
             ):
        self.id = id #immutable, unique
        self.name = name #nonempty string
        self.description = description #nonempty string
        self.begin_datetime = begin_datetime #datetime object
        self.end_datetime = end_datetime #datetime object
        self.url = url #any string
        self.iface = iface #any string
        self.router = router #any string
        self.tags = tags #any string
    
    def __unicode__(self):
        return self.name + ", id: " + self.id
    
    def save(self):
        #to implement
        pass

def validate_event(event):
    """
    Always call this before saving an event!
    
    raises ValueError when there is some inconsistency
    """
    
    if (event.__class__ != Event):
        raise ValueError('Object is not of type Event')
    
    if is_empty_or_space(event.name):
        raise ValueError("'name' property cannot be empty.")
    if is_empty_or_space(event.description):
        raise ValueError("'description' property cannot be empty.")
    
    for tag in tagging.utils.parse_tag_input(event.tags):
        #normally commas are delimiters, but if they are between double-quotes they become tags
        if not tag.isalnum():
            raise ValueError('Tags must be alphanumeric [a-z][A-Z][0-9].')
    event.tags = format_tag_string(event.tags)
    if event.end_datetime < event.begin_datetime:
        raise ValueError('The end date cannot be before the begin date.')

def is_empty_or_space(input_string):
    return (input_string == None or input_string == '' or input_string.isspace())

def serialize_events(events):
    """
    Takes in an iterable set of events and returns a JSON string.
    """
    json_container = []
    for event in events:
        json_event = {}
        json_event['pk'] = event.id
        json_event['model'] = net_almanac.event 
        fields = {}
        fields['name'] = event.name
        fields['description'] = event.description
        fields['begin_datetime'] = event.begin_datetime.strftime("%Y-%m-%d %H:%M:%S")
        fields['end_datetime'] = event.end_datetime.strftime("%Y-%m-%d %H:%M:%S")
        fields['url'] = event.url
        fields['iface'] = event.iface
        fields['router'] = event.router
        fields['tags'] = event.tags
        json_event['fields'] = fields
        json_container.append(json_event)
        
    return 

def deserialize_events(json_string):
    """
    Takes in a json_string and returns a list of Events
    """
    json_content = simplejson.loads(json_string)
    
    to_return = []
    for json_event in json_content:
        fields = json_event['fields']
        e = Event(json_event['pk'],
                  fields['name'],
                  fields['description'],
                  dateutil.parser.parse(fields['begin_datetime']),
                  dateutil.parser.parse(fields['end_datetime']),
                  fields['url'],
                  fields['iface'],
                  fields['router'],
                  fields['tags'])
        to_return.append(e)
    return to_return
                      
    
def get_all_events(url):
    """
    given the root URL of a net_almanac server, such as 
    
    http://www.example.com/net_almanac/event/
    
    returns a list of Events
    """
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = JSON_HEADERS)
    
    return deserialize_events(content)