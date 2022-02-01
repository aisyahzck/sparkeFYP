from django.db import models
from django.forms import ModelForm

# Create your models here. (for defining data model)

class Enquiry_log(models.Model):
    logID = models.IntegerField()
    date = models.DateField()
    model = models.CharField(max_length=20)
    parts = models.CharField(max_length=100)

class Enquiry_customer(models.Model):
    phoneNo = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
