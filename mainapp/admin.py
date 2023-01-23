from django.contrib import admin
from .models import Brocker, Trade, ImportTrade, MergedTrade

admin.site.register(Brocker)
admin.site.register(Trade)
admin.site.register(ImportTrade)
admin.site.register(MergedTrade)
