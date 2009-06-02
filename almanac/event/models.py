from django.db import models

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
    

class Tag(models.Model):
    #Python will throw a sneaky error that is difficult to catch if we have two Tags
    #of the same name.  So be sure to validate input before calling save().
    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    def __unicode__(self):
        return self.name

class TagAssignment(models.Model):
    event = models.ForeignKey(Event)
    tag = models.ForeignKey(Tag)
    def __unicode__(self):
        return str(self.event) + ", " +str(self.tag)