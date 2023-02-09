from datetime import datetime, date
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.conf import settings
from .consts import DEFUALT_RULE

TRADE_HISTORY_TYPE = (
    (0, 'Import'),
    (1, 'Sync'),
    (2, 'Manual')
)

class Brocker(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    desc = RichTextField()

    rules = models.TextField(default=DEFUALT_RULE)

    def __str__(self):
        return self.name

class TradeHistory(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="merged_trades")
    merged_trades = models.FilePathField(path=settings.MERGED_TRADES_PATH)
    output_trades = models.FilePathField(path=settings.OUTPUT_TRADES_PATH)
    brocker = models.ForeignKey(Brocker, on_delete=models.CASCADE, null=True)
    type = models.IntegerField(choices=TRADE_HISTORY_TYPE, default = 0)
    no_trades = models.IntegerField(default= 0)
    no_executions = models.IntegerField(default= 0)
    is_demo = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return f"{self.user.username}: {self.brocker} ({self.type})"

    