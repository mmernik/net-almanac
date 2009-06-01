from django.db import models

# Create your models here.
class Event(models.Model):
    name= models.CharField(max_length=200)
    
    description = models.CharField(max_length=200)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    def __unicode__(self):
        return self.name