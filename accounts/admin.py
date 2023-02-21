from django.contrib import admin
from .models import EarlyAccessUser, Profile, Portfolio

admin.site.register(EarlyAccessUser)
admin.site.register(Profile)
admin.site.register(Portfolio)