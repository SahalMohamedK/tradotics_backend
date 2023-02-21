from django.db import models
from mainapp.models import Brocker
from django.contrib.auth.models import User

class EarlyAccessUser(models.Model):
    name = models.CharField(max_length=130, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    whatsapp = models.CharField(max_length=13, blank=True, null=True)
    brocker = models.ForeignKey(Brocker, on_delete=models.CASCADE,  blank=True, null=True)
    segment = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to='early_access_files', blank=True, null=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    phoneNumber = models.CharField(max_length=13, blank=True, null = True)
    picture = models.ImageField(upload_to='profile_pics', blank= True, null = True)

    def __str__(self):
        return str(self.user)

class Portfolio(models.Model):    
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=225)
    value = models.DecimalField(decimal_places=2, max_digits=10)
    