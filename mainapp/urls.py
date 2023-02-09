from django.urls import path

from .views import *

urlpatterns = [
    path('brockers', brockerNamesView, name='list-brockers'),
    path('brocker/<id>', brockerDetailsView, name='list-brockers'),
    path('trades/import', import_trades_view, name='import-trades'),
    path('trades/filters', filters_view, name='filters-trades'),
    path('trades/histories', trade_histories_view, name='trade-histories'),
    path('trades/history/<id>', trade_history_view, name='trade-history'),
    path('trades/delete/histories', trade_delete_histories_view, name='trade-histories'),
    path('dashboard', dashboard_view, name='dashboard-view'),
    path('detailed-report', detailed_report_view, name='detailed-report-view'),
    path('trades', trades_view, name='trades-view'),
    path('trades-table', trades_table_view, name='trades-view'),
    path('trade/update', trade_update_view, name='trade-update'),
    path('trade/get/<id>', trade_view, name='trade-view'),
    path('calender-views', calender_views, name='calender-views'),
    path('compare', compare_views, name='compare'),
]
