from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets

import tagging
from tagging.fields import TagField
import logging
import datetime

MAX_LENGTH_FIELD = 100
MAX_LENGTH_DESCRIPTION = 500

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_FIELD)
    description = models.CharField(max_length=MAX_LENGTH_DESCRIPTION)
    begin_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    url = models.CharField(max_length=MAX_LENGTH_FIELD)
    
    tags = TagField()
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/net_almanac/event/"+str(self.id) + "/"

class EventForm(ModelForm):
    #NOTE: we need to manually set date
    begin_date = forms.DateField()
    begin_time = forms.TimeField()
    end_date = forms.DateField()
    end_time = forms.TimeField()
    
    
    class Meta:
        model = Event
        #These are split up into two fields, one for date and one for time.
        exclude = ('begin_datetime','end_datetime',)
        
    class Media:
        js = ('/site_media/js/scw.js',)
        
    def __init__(self, *args, **kwargs):
        #One static variable here is self.instance, which is the event this Form should model.
        super(EventForm,self).__init__(*args,**kwargs)
        logger = logging.getLogger('EventForm')
        logger.debug('constructing new EventForm')
        
        self.fields['description'].widget = forms.Textarea()
        
        self.fields['url'].required = False
        self.fields['end_time'].required = False
        self.fields['begin_time'].required = False
        
        self.fields['begin_date'].widget = forms.TextInput(attrs={'onclick':'scwShow(this,event);'})
        self.fields['end_date'].widget = forms.TextInput(attrs={'onclick':'scwShow(this,event);'})
        
        if (self.instance.name != ''):
            self.initial['begin_date'] = self.instance.begin_datetime.strftime("%Y-%m-%d") 
            self.initial['begin_time'] = self.instance.begin_datetime.strftime("%H:%M:%S")
            
            self.initial['end_date'] = self.instance.end_datetime.strftime("%Y-%m-%d") 
            self.initial['end_time'] = self.instance.end_datetime.strftime("%H:%M:%S")
        else:
            self.initial['begin_date'] = datetime.date.today().strftime('%Y-%m-%d')
            self.initial['end_date'] = datetime.date.today().strftime('%Y-%m-%d')
        
        self.fields['name'].widget.attrs['title'] = 'The name of the event.  Must be non-empty.'
        self.fields['name'].help_text = '*required'
        self.fields['description'].widget.attrs['title'] = 'A description of this event.  Must be non-empty.'
        self.fields['description'].help_text = '*required'
        self.fields['url'].widget.attrs['title'] = 'This field is optional.'
        self.fields['tags'].widget.attrs['title'] = 'A list of alphanumeric tags.  This field is optional.'
        self.fields['tags'].help_text = 'Use spaces to separate tags.'
        self.fields['begin_date'].widget.attrs['title'] = 'This field is required.'
        self.fields['begin_date'].help_text = 'Use YYYY-MM-DD format.'
        self.fields['end_date'].widget.attrs['title'] = 'This field is required.'
        self.fields['end_date'].help_text = 'Use YYYY-MM-DD format.'
        self.fields['begin_time'].widget.attrs['title'] = 'This field is optional.'
        self.fields['begin_time'].help_text = 'Use HH:MM[:ss] format.'
        self.fields['end_time'].widget.attrs['title'] = 'Please use HH:MM[:ss] format. This field is optional.'
        self.fields['end_time'].help_text = 'Use HH:MM[:ss] format.'
        