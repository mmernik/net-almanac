
****************************************************
*                    Net-Almanac                   *
*                 an ESnet project                 *
****************************************************

Contents
(0) About this document
(1) Introduction
(2) Installation Instructions 
(2.1) Running Instructions
(3) Interfacing with Programs
(3.1) REST interface
(3.2) using almanac_api.py
(4) Notes for devs
(5) licensing stuff, credits

0. ** About this document **
This document contains some notes to run the server and how to interface
net-almanac with other programs.  This project is hosted at:

http://code.google.com/p/net-almanac/


1. ** Introduction **
Almanac is a django web application that keeps track of time-stamped events.  
ESnet (www.es.net), a networking group, needed a simple tool to keep track of 
various network-related events.  The tool could used to spot future problems 
(such as conflicting events) or historical trends on the network.  This could
then be used to diagnose traffic anomalies.  However, Almanac can be used to 
keep track of any time-stamped data.  Users can view and manage events through
two interfaces: through browser HTML or the REST interface detailed in this
README document.  The URLs between the two interfaces are largely the same, so
one can directly view an event by browsing to the same URL that the REST 
interface is using.


2. ** Installation Instructions **

Dependencies to run the server are:
python 2.5
django v1.0
tags v0.3

For testing, dependencies are:
twill v0.9
wsgi_intercept
httplib2

Before you run, you need to install django v1.0: 
http://www.djangoproject.com/download/
and tags v0.3:
http://code.google.com/p/django-tagging/
To install v0.3 of tags, you must sync to the latest branch (do not download 
the installer).  Use the command:
 
svn checkout http://django-tagging.googlecode.com/svn/trunk/ django-tagging-read-only

To get the code.  The revision number that Almanac was made for is 155.  
Follow directions and copy it into your Python site-packages directory (on 
Mac OS X, it is /Library/Python/2.5/site-packages/, for cygwin it is in 
/lib/python/site-packages').  This is the same directory where django is
installed.

twill v0.9 , httplib2, wsgi-intercept, and simplejson are needed for running tests.  
They are available here:
http://twill.idyll.org/
http://code.google.com/p/httplib2/
http://code.google.com/p/wsgi-intercept/
http://www.undefined.org/python/

You might need to install dateutils depending on the version of python you
have.  Get it here:

http://labix.org/python-dateutil

All of the module dependencies are available through easy_install except for 
tagging v0.3, which you must checkout using svn.

2.1. ** Running Instructions **

Run 'python manage.py syncdb' to sync the database and load the data.  Note 
this command will overwrite your local database, or create a new one if there
is none.
Run 'python manage.py test' to run unit tests.
Run 'python manage.py runserver' to run the server.  Navigate to 

http://localhost:8000/net_almanac/

to view the homepage.


3. ** Interfacing with programs **

If the http header "accept" contains the string "application/json", then we
will return a JSON response.  Otherwise it will return the HTML response.

The API for JSON objects-
A typical JSON event example is below.  Note that we do not need to use a
pretty format if not convenient:
<begin JSON>
[{
	  "pk":1,
	  "model":"net_almanac.event",
	  "fields":{
		     "name":"experiment",
		     "tags":"lbnl experiment",
		     "url":"http://www.lbl.gov",
		     "end_datetime":"2009-06-03 15:01:01",
		     "begin_datetime":"2009-06-01 12:21:15",
		     "description":"a physics experiment"
	  }
}]
<end JSON>

"pk": the object's id in the database.  It must be an integer and unique. When
creating a new object, this value may be null.  If so, an id will be
automatically assigned.

"model": the name of the object request.  Only "net_almanac.event" is 
implemented so far.

"name": a name for the event.  Must be a non-empty string (does not need to
be unique).

"url": a URL link for more information.  Can be any string.

"description": a human-readable description of the event.  Must be a non-empty
string.

"tags": a space-delimited list of tags.  The server will automatically parse
any input string into this format.  See tagging documentation for more detail
on this.  This must not contain the characters: [[&$+,;#+"]]

"begin_datetime" and "end_datetime": ISO 8601-formatted dates using
YYYY-MM-DD [HH:MM:SS].  If the input string isn't as precise, the server will
generate the rest.  The end datetime cannot be before the begin datetime.

3.1. ** REST api **

URLs where JSON requests are accepted.  The header "accept" must contain the
JSON MIME "application/json" or the server will render HTML.

   -URL /net_almanac/event/
      -POST creates a new event from the JSON object in request
         -You must provide an unused id
      -GET returns all known events as JSON objects
      
   -URL /net_almanac/event/<id>/
      -PUT updates the event in the db from the JSON object in request
         -The id in the request must match the id in the URL
      -DELETE deletes the event from the db
      -GET returns a single event as a JSON object
      
   -URL /net_almanac/event/?<key1>=<value1>&<key2>=<value2>
      -GET returns all events filtered, the rules are below
      
The list of possible keys for GET filtering:
+----------------------+-------------------------------------------------------
|name                  | Returns events whose name contains the value
+----------------------+-------------------------------------------------------
|description           | Returns events whose description contains the value
+----------------------+-------------------------------------------------------
|search                | Returns events whose name, description, url, or tags
|                      | contains the value.
+----------------------+-------------------------------------------------------
|tag                   | Returns all events with this tag.  You can have more
|                      | than one.
+----------------------+-------------------------------------------------------
|date                  | Returns all events that fall at least partially on 
|                      | this date.  Use format YYYY-MM-DD.
+----------------------+-------------------------------------------------------
|begin_date & end_date | Returns all events that fall in between these two
|                      | dates. Use format YYYY-MM-DD.
+----------------------+-------------------------------------------------------
      
Different GET queries can be mixed together for more precise filtering.  Both 
the field 'begin_date' and 'end_date' are required; if one is missing the
server will ignore the other one.

The URL of all valid GET queries is also a valid HTML page.  Navigate to it
with your web browser to view the events in a human-usable UI.

3.2. ** Using almanac_api.py **

almanac_api.py is a python-based API for almanac.  It uses no code from the
main branch; just add it to your python path to install.  

It requires the httplib2 and simplejson packages.

Here is the structure:

Event: An object corresponding to one event.  Its fields are slightly
different from the JSON object outlined above:

  id: same as JSON 'pk' field.  Use the python None value when creating a new
  event.
  
  name, description, url: same rules as JSON apply here.
  
  tags: a python list of strings instead of a space-delimited string.
  
  begin_datetime, end_datetime: a datetime object.


NetAlmanac: An object that stores the URL of the server.  This has several
methods, all of which correspond to a particular http query:

  get_all_events(): Accesses the server and returns a list of Event objects.
  
  get_event(event_id): Returns only the event with this id as an Event object.
  
  get_filtered_events(args): Creates a corresponding GET filter request with the
  same parameters allowed in the previous section (name, search, etc.)
  
  save_event(event): saves a pre-existing event.
  
  delete_event(event): deletes an event.
  
  create_event(event): creates a new event in the database.
  
 
There are also a few utility functions:

validate(event): Checks an event for basic value errors.

deserialize_event(json_string): takes in a JSON string from the server and 
creates a list of Events.

serialize_event(events): Takes in a list of Events and returns a JSON string.

An example implementation of almanac_api.py is example/config_changes.py.  Run
it by simply typing
'python config_changes.py'
into the terminal while the development server is running.

4. ** Notes for devs **

Almanac was build alongside a thorough logging and testing framework provided
by django.  Logs are automatically written to logs/almanac_logs.out. Specific 
logging settings can be changed in settings.py.  Almanac also has a large set
of unit tests in net_almanac/tests.py.

The HTML interface has been tested against and works in:
IE7, IE8, Opera, Chrome, Firefox, Safari.

IE6 has a few cosmetic bugs, but is still functional.

5. ** licensing stuff, credits **

Net-Almanac was written by Andrew Wang (andrew_wang@berkeley.edu) under the
supervision of Jon Dugan from ESnet.

This project uses several open-source projects:
django v1.0
http://www.djangoproject.com/
BSD license

django tagging library v0.3
http://code.google.com/p/django-tagging/
MIT License

twill v0.9
http://twill.idyll.org/
MIT License

Simple Calendar Widget by Anthony Garrett
http://www.tarrget.info/calendar/scw.htm
GNU Lesser General Public License

HttpLib2
http://code.google.com/p/httplib2/
MIT License

WSGI-intercept
http://code.google.com/p/wsgi-intercept/
MIT license

SortTable
http://www.kryogenix.org/code/browser/sorttable/
MIT License

Simile_Widgets Timeline
http://code.google.com/p/simile-widgets/
New BSD License

