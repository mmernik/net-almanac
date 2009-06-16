
Some notes to run the server. 

Dependencies are:
django v1.0
tags v0.3
twill v0.9


** Installation Instructions **
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

twill v0.9  and httplib2 are needed for running tests.  They are available
here:
http://twill.idyll.org/
http://code.google.com/p/httplib2/

You might need to install dateutils depending on the version of python you
have.  Get it here:

http://labix.org/python-dateutil

and put it in the same directory as tags.


** Running Instructions **

Run 'python manage.py syncdb' to sync the database and load the data.  Note 
this command will overwrite your local database, or create a new one if there
is none.
Run 'python manage.py test' to run unit tests.
Run 'python manage.py runserver' to run the server.  Navigate to 

http://localhost:8000/event/

to view the homepage.


** Interfacing with programs **

If the http header "accept" contains the string "application/json", then we
will return a JSON response.  Otherwise it will return the HTML response.

The API for JSON objects-
A typical JSON event example is below.  Note that we do not need to use a
pretty format if not convenient:
<begin JSON>
[{
	  "pk":1,
	  "model":"event.event",
	  "fields":{
		     "iface":"Ethernet0",
		     "name":"experiment",
		     "tags":"lbnl, experiment",
		     "url":"http://www.lbl.gov",
		     "end_datetime":"2009-06-03 15:01:01",
		     "begin_datetime":"2009-06-01 12:21:15",
		     "router":"router1",
		     "description":"a physics experiment"
	  }
}]
<end JSON>

"pk": the object's id in the database.  It must be an integer and unique.

"model": the name of the object request.  Only "event.event" is implemented
so far.

"name": a name for the event.  Must be a non-empty string (does not need to
be unique).

"iface": the interface.  Can be any string.

"url": a URL link for more information.  Can be any string.

"router": the router where the event occurs.  Can be any string.

"description": a human-readable description of the event.  Must be a non-empty
string.

"tags": a comma-delimited list of tags.  The server will automatically parse
any input string into this format.  See tagging documentation for more detail
on this.

"begin_datetime" and "end_datetime": ISO 8601-formatted dates using
YYYY-MM-DD [HH:MM:SS].  If the input string isn't as precise, the server will
generate the rest.  The end datetime cannot be before the begin datetime.

URLs where JSON requests are accepted.  The header "accept" must contain the
JSON MIME "application/json" or the server will render HTML.

   -URL /event/
      -POST creates a new object from JSON object in request
         -You must provide an unused id
      -GET returns all known objects as JSON
      
   -URL /event/<id>/
      -PUT updates the object in the db from the JSON object in request
         -The id in the request must match the id in the URL
      -DELETE deletes the object from the db
      -GET returns a single JSON object
      
   -URL /event/tags/<id>/
      -GET returns all objects with this tag in JSON

** licensing stuff, credits **

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

SortTable
http://www.kryogenix.org/code/browser/sorttable/
MIT License

