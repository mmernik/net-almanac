from django.db import models
from django import forms
from django.forms import ModelForm

import tagging
import logging


MAX_LENGTH=200

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=MAX_LENGTH)
    description = models.CharField(max_length=MAX_LENGTH)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    url = models.CharField(max_length=MAX_LENGTH)
    router = models.CharField(max_length=MAX_LENGTH)
    iface = models.CharField(max_length=MAX_LENGTH)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/event/"+str(self.id) + "/"

class EventForm(ModelForm):
    #TODO: add date widget
    tags = forms.CharField(max_length=MAX_LENGTH)
    
    class Meta:
        model = Event

try:
    logging.info('Loading models for a new instance.  Registering models')
    tagging.register(Event)
except tagging.AlreadyRegistered:
    # Dev Note: Not sure the right way to register a model for tagging b/c it
    # raises this error if registered more than once. We end up registering
    # the first time during "manage.py syncdb" and then a second time when
    # actually attempting to run the site.
    pass
