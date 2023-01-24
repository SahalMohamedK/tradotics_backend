from datetime import datetime, date
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .consts import PNL_STATUS, TRADE_TYPE, DEFUALT_FIELDS_RULE,\
    DEFUALT_ASSETS_RULE, DEFUALT_OPTIONS_RULE, OPTIONS_TYPE, ASSETS_TYPE, SUPPORTED_FILE_TYPES

class Brocker(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    desc = RichTextField()

    fields_rule = models.TextField(default=DEFUALT_FIELDS_RULE)
    assets_rule = models.TextField(default=DEFUALT_ASSETS_RULE)
    options_rule = models.TextField(default=DEFUALT_OPTIONS_RULE)

    def __str__(self):
        return self.name

class Trade(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="merged_trades")
    merged_trades = models.FilePathField(path=settings.MERGED_TRADES_PATH)
    output_trades = models.FilePathField(path=settings.OUTPUT_TRADES_PATH)
    brocker = models.ForeignKey(Brocker, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.brocker}"