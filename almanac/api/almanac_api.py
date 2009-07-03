import datetime
import httplib2
import simplejson
import dateutil.parser

"""
A python interface to almanac's REST requests.
This shouldn't refer to any files in the main branch.
"""


HTTP_OK = 200
JSON_HEADERS = {'accept':'application/json'}


MAX_LENGTH_FIELD = 100
MAX_LENGTH_DESCRIPTION = 500
FORBIDDEN_CHARS = ['&','$','+',',',';','#','+','"',' ','\t']


class NetAlmanac():
    """
    given the root URL of a net_almanac server, such as 
    
    http://www.example.com/net_almanac/event/
    """
    def __init__(self, url):
        self.url = url

    def get_all_events(self):
        """
        returns a list of Events
        """
        http = httplib2.Http()
        response, content = http.request(self.url, 'GET', headers = JSON_HEADERS)
        return deserialize_events(content)
    
    def get_event(self, event_id):
        """
        returns one Event with the specific id.  Will return None if there is no Event.
        """
        http = httplib2.Http()
        response, content = http.request(self.url + str(event_id) + '/', 'GET', headers = JSON_HEADERS)
        if response.status == 404:
            return None
        return deserialize_events(content)[0]
    
    def get_filtered_events(self,
                            search=None,
                            name=None,
                            description=None,
                            tags=None,
                            date=None,
                            begin_date=None,
                            end_date=None):
        http = httplib2.Http()
        
        filters = []
        if search:
            filters.append("search=" + search)
        if name:
            filters.append("name=" + name)
        if description:
            filters.append("description=" + description)
        if date:
            filters.append("date=" + date.strftime('%Y-%M-%d'))
        if begin_date:
            filters.append("begin_date=" + begin_date.strftime('%Y-%M-%d'))
        if end_date:
            filters.append("end_date=" + end_date.strftime('%Y-%M-%d'))
        
        if tags:
            for tag in tags:
                filters.append("tag=" + tag)
        
        url = self.url + "?" + "&".join(filters)
        
        response, content = http.request(url, 'GET', headers = JSON_HEADERS)
        return deserialize_events(content)
    
    def save_event(self,
                   event):
        http = httplib2.Http()
       
        input = serialize_events([event])
        response, content = http.request(self.url + str(event.id) + '/', 'PUT', input, headers = JSON_HEADERS)
        
        if response.status != HTTP_OK:
            raise ValueError('Event not saved correctly. Message from server: ' + content)
        
    def create_event(self,
                     event):
        http = httplib2.Http()
       
        input = serialize_events([event])
        response, content = http.request(self.url , 'POST', input, headers = JSON_HEADERS)
        
        if response.status != HTTP_OK:
            raise ValueError('Event not created correctly. Message from server: ' + content)
        
    def delete_event(self,
                     event):
        http = httplib2.Http()
        response, content = http.request(self.url + str(event.id) + '/' , 'DELETE', headers = JSON_HEADERS)
        
        if response.status != HTTP_OK:
            raise ValueError('Event not deleted correctly. Message from server: ' + content)
        

class Event():
    """
    An event represents one event object in the almanac database.
    See README.txt for more information.  This is a local object, we need to
    call functions save_event or create_event to modify the database with it.
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
    
    def __str__(self):
        return self.name + ", id: " + str(self.id)
    

def validate_event(event):
    """
    Always call this before saving an event!
    
    raises ValueError when there is some inconsistency
    """
    
    if is_empty_or_space(event.name):
        raise ValueError("'name' property cannot be empty.")
    if is_empty_or_space(event.description):
        raise ValueError("'description' property cannot be empty.")
    
    if (len(event.name) > MAX_LENGTH_FIELD
        or len(event.url) > MAX_LENGTH_FIELD
        or len(event.router) > MAX_LENGTH_FIELD
        or len(event.iface) > MAX_LENGTH_FIELD
        or len(event.description) > MAX_LENGTH_DESCRIPTION):
        raise ValueError("Field data too long")
    
    if not is_valid_tag(event.tags):
        raise ValueError('Tags cannot contain whitespace or any special symbols: [\'&"$+,;#+]')
    
    if event.end_datetime < event.begin_datetime:
        raise ValueError('The end date cannot be before the begin date.')
    
    return True    

def serialize_events(events):
    """
    Takes in an iterable set of events and returns a JSON string.
    """
    json_container = []
    for event in events:
        json_event = {}
        json_event['pk'] = event.id
        json_event['model'] = 'net_almanac.event' 
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
    
    return simplejson.dumps(json_container)

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
    
        
def is_empty_or_space(input_string):
    return (input_string == None or input_string == '' or input_string.isspace())

#We won't parse tags like in views.py, so allow whitespaces.
def is_valid_tag(tag_string):
    for char in tag_string:
        if char == ' ':
             continue
        for c in FORBIDDEN_CHARS:
            if c == char:
                return False
    return True
    