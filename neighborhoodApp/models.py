from django.db import models
from django.core.validators import *
from django.db.models import JSONField
import datetime

#from geohash import *

# Create your models here.

#defalt is 1day in the future
def defaultExpireAt():
    return datetime.datetime.now() + datetime.timedelta(hours=1)

def defaultGeohashList():
    return {"geohashList": ["default"]}

class Users(models.Model):
    mail = models.CharField(max_length=30)
    expire = models.PositiveSmallIntegerField(default=24, validators=[MaxValueValidator(720), MinValueValidator(1)]) #in hours
    expire_at = models.DateTimeField(default = datetime.datetime.now(), null=True)

    longitude = models.IntegerField(default=0)
    latitude = models.IntegerField(default=0)
    geohash = models.CharField(default=0, max_length=30)
    #geohash_length = models.IntegerField(default=6)
    #neighberhood_layers = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(10), MinValueValidator(0)])

    geohashList = JSONField(default=defaultGeohashList)



    #save mathode überschreiben, um geohash aus Long/Lat zu berechnen

    # @property
    # def hash(self):
    #     return encode(self.latitude,self.longitude, self.accuracy)

    # def save (self, *args, **kwarg):
    #     self.geohash = self.hash
    #     super(Users, self).save( *args, **kwarg)

    def __str__(self):
        return self.mail

#   if change models.py:
#   python3 manage.py makemigrations
#   python3 manage.py migrate

