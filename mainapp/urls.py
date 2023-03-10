from django.urls import path

from .views import *

urlpatterns = [
    path('brockers', brockerNamesView),
    path('brocker/<id>', brockerDetailsView),
    path('trades/import', import_trades_view),
    path('trades/manual', manual_trade_view),
    # path('execution/manual', manual_execution_view),
    path('trades/filters', filters_view),
    path('trades/histories', trade_histories_view),
    path('trades/history/<id>', trade_history_view),
    path('trades/delete/histories', trade_delete_histories_view),
    path('dashboard', dashboard_view),
    path('trades-table', trades_table_view),
    path('detailed-report', detailed_report_view),
    path('views/days', day_views_view),
    path('views/calenders', calender_views_view),
    path('views/trades', trades_view),
    path('compare', compare_view),
    path('comparison/create', save_comparison_view),
    path('comparison/get', comparisons_view),
    path('trade/get/<id>', trade_view),
    path('trade/update', trade_update_view),
    path('orders/get/<id>', orders_view),
    path('order/update', order_update_view),
    path('portfolio/edit', edit_portfolio_view),
    path('portfolio/get', portfolio_view),
    path('portfolio/delete', delete_portfolio_view),
    path('portfolio/add', add_portfolio_view),
    path('add-adustment', add_adjustment_view),
    path('symbols', symbols_view),
    path('test', test_view),
]
