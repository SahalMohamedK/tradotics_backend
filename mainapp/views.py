import pandas as pd
import os
import hashlib
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializers import BrockerNamesSerializer, BrockerSerializer, ImportTradesSerializer, FiltersQuarySerializer, \
    FiltersSerializer, CompareQuerySerializer, TradeHistrotySerializer, TradeTableQuerySerializer, PaginationQuarySerializer,\
    TradeSerializer, OrderSerializer, ComparisonSerialiser
from .models import Brocker, TradeHistory, Comparison
from django.conf import settings
from .consts import ERROR
from .responses import success
from .trades import MergedTrades, OutputTrades, Trades, Orders
from .trades import fields

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def filters_view(request):
    user = request.user    
    trades = Trades(user)
    filters = trades.filters.get()
    filters_serializer = FiltersSerializer(data = filters)
    if filters_serializer.is_valid():
        return Response(filters_serializer.data, status=status.HTTP_200_OK)
    return Response(filters_serializer.errors, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trades_table_view(request):
    user = request.user
    pagination_query_serializer = PaginationQuarySerializer(data = request.data)
    if pagination_query_serializer.is_valid():
        filters = pagination_query_serializer.data['filters']
        start = pagination_query_serializer.data['start']
        size = pagination_query_serializer.data['size']
        trades = Trades(user)
        trades.filters.apply(filters)
        data = trades.get([fields.trades(start, size)])
        return Response(data, status=status.HTTP_200_OK)
    return Response(pagination_query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def open_trades_table_view(request):
    user = request.user
    trade_table_query_serializer = TradeTableQuerySerializer(data = request.data)
    if trade_table_query_serializer.is_valid():
        filters = trade_table_query_serializer.data['filters']
        start = trade_table_query_serializer.data['start']
        size = trade_table_query_serializer.data['size']
        trades = Trades(user)
        trades.filters.apply(filters)
        data = trades.get([fields.trades(start, size)])
        return Response(data, status=status.HTTP_200_OK)
    return Response(trade_table_query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def dashboard_view(request):
    user = request.user
    filter_serializer = FiltersQuarySerializer(data = request.data)
    if filter_serializer.is_valid():
        filters = filter_serializer.data
        layout = [
            fields.isDemo(),
            fields.cumulativePnl(),
            fields.totalPnl(),
            fields.counts(),
            fields.countsByDay(),
            fields.pnlByDates(),
            fields.pnlByStatus(),
            fields.pnlByDays(),
            fields.pnlByMonths(),
            fields.pnlBySetup(),
            fields.pnlByHours(),
            fields.pnlByDuration(),
            fields.dialyPnl(),
            fields.openTrades(),
            fields.insights()
        ]
        trades  = Trades(user)
        trades.filters.apply(filters)
        data = trades.get(layout)
        return Response(data, status=status.HTTP_200_OK)
    return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def detailed_report_view(request):
    user = request.user
    filter_serializer = FiltersQuarySerializer(data = request.data)
    if filter_serializer.is_valid():
        filters = filter_serializer.data
        trades = Trades(user)
        trades.filters.apply(filters)
        layout = [
            fields.counts(),
            fields.pnlByTradeTypes(),
            fields.pnlByStatus(),
            fields.totalQuantity(),
            fields.dateWise(),
            fields.maxConsec(),
            fields.counts(),
            fields.countsByRoi(),
            fields.countsByDay(),
            fields.openAndClose(),
            fields.highestPnlTrade(),
            fields.lowestPnlTrade(),
            fields.holdTimes(),
            fields.dataByExpiryDate(),
            fields.dayDistribution(),
            fields.hourDistribution(),
            fields.setupDistribution(),
            fields.durationDistribution(),
            fields.costDistribution(),
            fields.priceDistribution(),
            fields.symbolDistribution()
        ]
        data = trades.get(layout)
        return Response(data, status=status.HTTP_200_OK)
    return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def day_views_view(request):
    user = request.user
    pagination_query_serializer = PaginationQuarySerializer(data = request.data)
    if pagination_query_serializer.is_valid():
        filters = pagination_query_serializer.data['filters']
        start = pagination_query_serializer.data['start']
        size = pagination_query_serializer.data['size']
        trades = Trades(user)
        trades.filters.apply(filters)
        layout = [
            fields.dataByDates(start, size),
            fields.totalDates('total')
        ]
        data = trades.get(layout)
        return Response(data, status=status.HTTP_200_OK)
    return Response(pagination_query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def calender_views_view(request):
    user = request.user
    filters_quary_serializer = FiltersQuarySerializer(data = request.data)
    if filters_quary_serializer.is_valid():
        filters = filters_quary_serializer.data
        trades = Trades(user)
        trades.filters.apply(filters)
        layout = [
            fields.pnlByDates()
        ]
        data = trades.get(layout)
        return Response(data, status=status.HTTP_200_OK)
    return Response(filters_quary_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trades_view(request):
    user = request.user
    filter_serializer = FiltersQuarySerializer(data = request.data)
    if filter_serializer.is_valid():
        filters = filter_serializer.data
        trades = Trades(user)
        trades.filters.apply(filters)
        layout = [
            fields.highestPnlTrade(),
            fields.lowestPnlTrade(),
            fields.counts()
        ]
        data = trades.get(layout)
        return Response(data, status=status.HTTP_200_OK)
    return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def compare_view(request):
    user = request.user
    compare_serializer = CompareQuerySerializer(data = request.data)
    if compare_serializer.is_valid():
        filters1 = compare_serializer.data['filters1']
        filters2 = compare_serializer.data['filters2']
        trades1 = Trades(user)
        trades2 = Trades(user)
        trades1.filters.apply(filters1)
        trades2.filters.apply(filters2)
        layout = [
            fields.counts(),
            fields.highestPnlTrade(),
            fields.lowestPnlTrade(),
            fields.cumulativePnl(),
            fields.dialyPnl(),
            fields.pnlByDays(),
            fields.pnlByMonths(),
            fields.pnlByDuration(),
            fields.profitFactor(),
            fields.pnlByStatus(),
            fields.pnlBySetup(),
            fields.pnlByHours(),
            fields.holdTimes()
        ]
        data1 = trades1.get(layout)
        data2 = trades2.get(layout)
        return Response({'data1': data1, 'data2': data2}, status=status.HTTP_200_OK)
    return Response(compare_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trade_view(request, id):
    user = request.user
    trades = Trades(user)
    layout = [
        fields.trade(id)
    ]
    data = trades.get(layout)
    if data['trade']['id'] == id:
        return Response(data, status=status.HTTP_200_OK)
    return Response({'code': ERROR.INVALIED_TRADE}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trade_update_view(request):
    user = request.user
    trade_serializer = TradeSerializer(data = request.data['trade'])
    if trade_serializer.is_valid():
        trade = trade_serializer.data
        trades = Trades(user)
        result = trades.update(trade)
        if result:
            return Response({'code': success.OK}, status=status.HTTP_200_OK)
        return Response({'code': ERROR.TRADE_UPDATE_FAILED}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(trade_serializer.erros, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def orders_view(request, id):
    user = request.user
    orders = Orders(user)
    layout = [
        fields.ordersByTrade(id, name='orders')
    ]
    data = orders.get(layout)    
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def save_comparison_view(request):
    user = request.user
    comparison_serializer = ComparisonSerialiser(data = request.data)
    if comparison_serializer.is_valid():
        data = comparison_serializer.data
        Comparison.objects.create(user = user, is_popular = False, **data)
        return Response({'code': success.OK}, status=status.HTTP_200_OK)
    return Response(comparison_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def comparisons_view(request):
    user = request.user
    comparison = Comparison.objects.filter(Q(user=user) | Q(is_popular=True))
    if comparison.exists():
        comparison_serializer = ComparisonSerialiser(comparison, many = True)
        return Response(comparison_serializer.data, status=status.HTTP_200_OK)
    return Response({'code': ERROR.NO_COMPARISON}, status=status.HTTP_204_NO_CONTENT)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# def order_update_view(request):
#     user = request.user
#     order_serializer = OrderSerializer(request.data)
#     if order_serializer.is_valid():
#         order = order_serializer.data
#         orders = Orders(user)
#         if orders.update(order):
#             return Response({'code': success.OK}, status=status.HTTP_200_OK)
#         return Response({'code': ERROR.TRADE_UPDATE_FAILED}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     return Response(order_serializer.erros, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# def trade_view(request, id):
#     user = request.user
#     trade_histories = TradeHistory.objects.filter(user = user)
#     trades = Trades(user)
#     if trade_histories.exists():
#         merged_trades = pd.DataFrame()
#         is_merged_trades = False
#         for trade_history in trade_histories:
#             merged_filename = trade_history.merged_trades
#             merged_trade = pd.read_csv(merged_filename)
#             if is_merged_trades:
#                 merged_trades = pd.concat([merged_trades, merged_trade]).drop_duplicates()
#             else:
#                 is_merged_trades = True
#                 merged_trades = merged_trade
#     if not merged_trades.empty:
#         orders = merged_trades[merged_trades['tradeId'] == id]
#         if not orders.empty:
#             orders = orders.to_dict('records')
#         else:
#             orders = []

#         trade = trades.get(id)
#         if trade:
#             entry = datetime.datetime.strptime(f"{trade['entryDate']} {trade['entryTime']}", '%Y-%m-%d %H:%M:%S')
#             exit = datetime.datetime.strptime(f"{trade['exitDate']} {trade['exitTime']}", '%Y-%m-%d %H:%M:%S')
#             data = {
#                 'trade': trade,
#                 'orders': orders,
#                 'duration': human_delta(exit-entry),
#             }
#             trade_serializer = TradeAnalyticsSerializer(data= data)
#             if trade_serializer.is_valid():
#                 return Response(trade_serializer.data, status=status.HTTP_200_OK)
#             return Response(trade_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response({'code': ERROR.NO_TRADE}, status=status.HTTP_400_BAD_REQUEST)
#     return Response({'code': ERROR.NO_TRADE_HISTORIES}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# def trade_update_view(request):
#     user = request.user
#     trade_update_serializer = TradeSerializer(data = request.data['trade'])
#     if trade_update_serializer.is_valid():
#         trade_update = trade_update_serializer.data
#         result = False
#         trade_histories = TradeHistory.objects.filter(user = user)
#         for trade_history in trade_histories:
#             if trade_history.pk == trade_update['tradeHistory']:
#                 output_trades = pd.read_csv(trade_history.output_trades)
#                 trade = output_trades[output_trades['id'] == trade_update['id']]
#                 index = trade.index[0]
#                 trade = trade.to_dict('records')[0]
#                 trade_update['setup'] = ','.join(trade_update['setup'])
#                 trade_update['mistakes'] = ','.join(trade_update['mistakes'])
#                 trade_update['tags'] = ','.join(trade_update['tags'])
#                 for column in trade_update:
#                     if column in trade and trade[column] != trade_update[column]:
#                         output_trades.loc[index, column] = trade_update[column]
#                 output_trades.to_csv(trade_history.output_trades, index=False)
#                 result = True
#                 break
#         if result:
#             return Response({'message': 'Success'}, status=status.HTTP_200_OK)
#         return Response({'message': 'Invalied trade updation'}, status=status.HTTP_400_BAD_REQUEST)
#     return Response(trade_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# def trade_delete_view(request):
#     user = request.user
#     trade_delete_serilizer = TradeSerializer(data = request.data)
#     if trade_delete_serilizer.is_valid():
#         data = trade_delete_serilizer.data
#         id = data['id']
#         trade_history_id = data['tradeHstory']
#         trade_history = TradeHistory.objects.get(pk = trade_history_id)
#         pd.read_csv(trade_history.output_trades)
#         pd.read_csv(trade_history.merged_trades)
#     return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def import_trades_view(request):
    serializer = ImportTradesSerializer(data = request.data)
    user = request.user
    if serializer.is_valid():
        brocker_id = serializer.data['brocker']
        brocker = Brocker.objects.get(id = brocker_id)
        
        file = serializer.validated_data['file']
        file_content = file.read()
        file.seek(0)
        filename = hashlib.md5(file_content+brocker.name.encode()+user.username.encode()).hexdigest()+'.csv'

        merged_filename = os.path.join(settings.MERGED_TRADES_PATH, filename)
        output_filename = os.path.join(settings.OUTPUT_TRADES_PATH, filename)
        merged_exists = os.path.exists(merged_filename)
        output_exists = os.path.exists(output_filename)
        if merged_exists and output_exists:
            return Response({'message': 'The file is already uploaded', 'type': 'warning', 'title': 'File exists'}, status=status.HTTP_400_BAD_REQUEST)
        elif merged_exists and not output_exists:
            os.remove(merged_filename)
        elif output_exists and not merged_exists:
            os.remove(output_filename)

        merged_trades = MergedTrades(brocker_rules=brocker.rules)
        merged_trades.load(file)
        if merged_trades.error:
            return Response({'message': merged_trades.error, 'type': 'error', 'title': 'Upload failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        output_trades = OutputTrades(merged_trades)
        output_trades.save(output_filename)
        merged_trades.save(merged_filename)
        trade = TradeHistory(user=request.user, merged_trades=merged_filename, output_trades=output_filename, brocker=brocker, no_trades = len(output_trades), no_executions = len(merged_trades))
        trade.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trade_histories_view(request):
    user = request.user
    trade_histories = TradeHistory.objects.filter(user = user, is_demo=False)
    if trade_histories.exists():
        trade_histories_serializer = TradeHistrotySerializer(trade_histories, many = True)
        return Response(trade_histories_serializer.data, status=status.HTTP_200_OK)
    return Response({'message': 'No trade history'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trade_delete_histories_view(request):
    user = request.user
    id = request.data['id']
    try:
        trade_history = TradeHistory.objects.get(user = user, id = id)
    except TradeHistory.DoesNotExist:
        trade_history = None
    if trade_history:
        trade_history.delete()
        os.remove(trade_history.output_trades)
        os.remove(trade_history.merged_trades)

        return Response({'message': 'Success'}, status=status.HTTP_200_OK)
    return Response({'message': 'No trade history'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trade_history_view(request, id):
    user = request.user
    try:
        trade_history = TradeHistory.objects.get(user = user, id = id)
    except TradeHistory.DoesNotExist:
        trade_history = None
    if trade_history:
        output_filename = trade_history.output_trades 
        with open(output_filename) as f:
            data = f.read()

        return Response({"file": data, 'filename': f'Tradotics_{trade_history.brocker.name}_{trade_history.created.strftime("%Y-%m-%d_%H-%M-%S")}.csv'}, status=status.HTTP_200_OK)
    return Response({'message': 'No trade history'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def brockerNamesView(request):
    brockers = Brocker.objects.all()
    serializer = BrockerNamesSerializer(brockers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def brockerDetailsView(request, id):
    brocker = Brocker.objects.get(id=id)
    serializer = BrockerSerializer(brocker)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def test_view(request):
    user = request.user
    layout = [
        fields.isDemo(),
        fields.cumulativePnl(),
        fields.totalPnl(),
        fields.counts(),
        fields.countsByDay(),
        fields.profitFactor(),
        fields.pnlByDates(),
        fields.pnlByTradeTypes(),
        fields.pnlByStatus(),
        fields.pnlByDays(),
        fields.pnlByMonths(),
        fields.pnlBySetup(),
        fields.pnlByDuration(),
    ]
    trades  = Trades(user)
    # trades.filters.apply(filters)
    data = trades.get(layout)
    return Response(data, status=status.HTTP_200_OK)
