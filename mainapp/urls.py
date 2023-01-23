from django.urls import path

from .views import *

urlpatterns = [
    path('brockers', brockerNamesView, name='list-brockers'),
    path('brocker/<id>', brockerDetailsView, name='list-brockers'),
    path('trades/import', importTradesView, name='import-trade'),
    path('trades', tradesView, name='import-trade'),
]
