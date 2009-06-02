from django.db import models
import tagging


MAX_LENGTH=200

# Create your models here.
class Event(models.Model):
    name= models.CharField(max_length=MAX_LENGTH)
    description = models.CharField(max_length=MAX_LENGTH)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    url = models.CharField(max_length=MAX_LENGTH)
    router = models.CharField(max_length=MAX_LENGTH)
    iface = models.CharField(max_length=MAX_LENGTH)
    
    def __unicode__(self):
        return self.name

try:
    tagging.register(Event)
except tagging.AlreadyRegistered:
    # Dev Note: Not sure the right way to register a model for tagging b/c it
    # raises this error if registered more than once. We end up registering
    # the first time during "manage.py syncdb" and then a second time when
    # actually attempting to run the site.
    pass
