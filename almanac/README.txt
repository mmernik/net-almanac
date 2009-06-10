Some notes to run the server.

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

You might need to install dateutils depending on the version of python you have.  
Get it here:

http://labix.org/python-dateutil

and put it in the same directory as tags.

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