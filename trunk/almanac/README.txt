Some notes to run the server.

Before you run, you need to install django v1.0: 
http://www.djangoproject.com/download/
and tags v0.3:
http://code.google.com/p/django-tagging/

Run 'python manage.py syncdb' to sync the database and load the data.  Note this command will overwrite your local database.

Run 'python manage.py test' to run unit tests.

Run 'python manage.py runserver' to run the server.