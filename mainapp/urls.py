from django.urls import path

from .views import *

urlpatterns = [
    path('brockers', brockerNamesView, name='list-brockers'),
    path('brocker/<id>', brockerDetailsView, name='list-brockers'),
    path('trades/import', uploadTradesView, name='import-trades'),
    path('trades/output', outputTradesView, name='output-trades'),
    path('trades/filters', filtersView, name='filters-trades'),
]
