from django.contrib import admin
from .models import Brocker, TradeHistory

class TradeHistoryAdmin(admin.ModelAdmin):
    model = TradeHistory
    list_display = ['user', 'brocker', 'type', 'no_trades', 'no_executions'] 

admin.site.register(Brocker)
admin.site.register(TradeHistory, TradeHistoryAdmin)
