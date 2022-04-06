from django.db import models
from django.core.validators import *
from django.db.models import JSONField
import datetime
from .config import *




def defaultExpireAt():
    # defalt is 1day in the future
    return datetime.datetime.now() + datetime.timedelta(hours=1)

def defaultGeohashList():
    return {"geohashList": ["default"]}

class Users(models.Model):
    mail = models.CharField(max_length=30)
    expire = models.PositiveSmallIntegerField(default=24, validators=[MaxValueValidator(720), MinValueValidator(1)]) #in hours
    expire_at = models.DateTimeField(default = datetime.datetime.now(), null=True)

    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    geohash = models.CharField(default=0, max_length=10, validators=[MinLengthValidator(geohash_length)])
    #geohash_length = models.IntegerField(default=6)
    #neighberhood_layers = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(10), MinValueValidator(0)])

    geohashList = JSONField(default=defaultGeohashList)



    def __str__(self):
        return self.mail

#   if change models.py:
#   python3 manage.py makemigrations
#   python3 manage.py migrate

