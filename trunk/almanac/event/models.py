from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets

import tagging
import logging
import datetime


MAX_LENGTH=200

DEFAULT_TIME = '12:00:00'
# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=MAX_LENGTH)
    description = models.CharField(max_length=MAX_LENGTH)
    begin_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    url = models.CharField(max_length=MAX_LENGTH)
    router = models.CharField(max_length=MAX_LENGTH)
    iface = models.CharField(max_length=MAX_LENGTH)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/event/"+str(self.id) + "/"

class EventForm(ModelForm):
    
    #NOTE: we need to manually set tags and dates
    
    begin_date = forms.CharField(max_length=MAX_LENGTH)
    begin_time = forms.CharField(max_length=MAX_LENGTH)
    end_date = forms.CharField(max_length=MAX_LENGTH)
    end_time = forms.CharField(max_length=MAX_LENGTH)
    
    tags = forms.CharField(max_length=MAX_LENGTH)
    
    class Meta:
        model = Event
        exclude = ('begin_datetime','end_datetime',)
        
    class Media:
        js = ('/site_media/scw.js',)
        
    def __init__(self, *args, **kwargs):
        super(EventForm,self).__init__(*args,**kwargs)
        
        logger = logging.getLogger('EventForm')
        
        self.fields['begin_date'].widget = forms.TextInput(attrs={'onclick':'scwShow(this,event);'})
        self.fields['end_date'].widget = forms.TextInput(attrs={'onclick':'scwShow(this,event);'})
        
        logger.info(tagging.utils.edit_string_for_tags(self.instance.tags))
        logger.info("self.instance: " + str(self.instance.name))
        
        self.initial['tags'] = tagging.utils.edit_string_for_tags(self.instance.tags)
        if (self.instance.name != ''):
            self.initial['begin_date'] = self.instance.begin_datetime.strftime("%Y-%m-%d") 
            self.initial['begin_time'] = self.instance.begin_datetime.strftime("%H:%M:%S")
            
            self.initial['end_date'] = self.instance.begin_datetime.strftime("%Y-%m-%d") 
            self.initial['end_time'] = self.instance.begin_datetime.strftime("%H:%M:%S")
        else:
            self.initial['begin_date'] = datetime.date.today().strftime('%Y-%m-%d')
            self.initial['begin_time'] = DEFAULT_TIME
            
            self.initial['end_date'] = datetime.date.today().strftime('%Y-%m-%d')
            self.initial['end_time'] = DEFAULT_TIME
        
        

        

try:
    logging.info('Loading models for a new instance.  Registering models')
    tagging.register(Event)
except tagging.AlreadyRegistered:
    # Dev Note: Not sure the right way to register a model for tagging b/c it
    # raises this error if registered more than once. We end up registering
    # the first time during "manage.py syncdb" and then a second time when
    # actually attempting to run the site.
    pass
