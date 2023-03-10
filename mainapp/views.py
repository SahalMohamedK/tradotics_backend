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
     CompareQuerySerializer, TradeHistrotySerializer, TradeTableQuerySerializer, PaginationQuarySerializer,\
    TradeSerializer, ComparisonSerialiser, PortfolioEntrySeriliser, PortfolioSeriliser, ManualTradeSerializer,\
    ManualExecutionSerializer, OrderSerializer
from .models import Brocker, TradeHistory, Comparison, Portfolio
from django.conf import settings
from .consts import ERROR
from .responses import success
from .trades import MergedTrades, OutputTrades, Trades, Orders
from rest_framework.views import APIView
from .trades import fields

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def filters_view(request):
    user = request.user    
    trades = Trades(user)
    data = trades.filters.get()
    return Response(data, status=status.HTTP_200_OK)

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
        data = trades.get([fields.trades(start, size)], filters)
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
            fields.pnlByMistakes(),
            fields.pnlByTags(),
            fields.pnlByHours(),
            fields.pnlByDuration(),
            fields.dialyPnl(),
            fields.openTrades(),
            fields.insights()
        ]
        trades  = Trades(user)
        data = trades.get(layout, filters)
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
            fields.tagsDistribution(),
            fields.mistakesDistribution(),
            fields.durationDistribution(),
            fields.costDistribution(),
            fields.priceDistribution(),
            fields.symbolDistribution()
        ]
        data = trades.get(layout, filters)
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
        layout = [
            fields.dataByDates(start, size),
            fields.totalDates('total')
        ]
        data = trades.get(layout, filters)
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
        layout = [
            fields.pnlByDates()
        ]
        data = trades.get(layout, filters)
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
        layout = [
            fields.highestPnlTrade(),
            fields.lowestPnlTrade(),
            fields.counts()
        ]
        data = trades.get(layout, filters)
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
        layout = [
            fields.counts(),
            fields.totalPnl(),
            fields.highestPnlTrade(),
            fields.lowestPnlTrade(),
            fields.cumulativePnl(),
            fields.dialyPnl(),
            fields.pnlByDays(),
            fields.pnlByMonths(),
            fields.pnlByDuration(),
            fields.profitFactor(),
            fields.pnlByStatus(),
            fields.pnlByTags(),
            fields.pnlByMistakes(),
            fields.pnlBySetup(),
            fields.pnlByHours(),
            fields.holdTimes()
        ]
        data1 = trades1.get(layout, filters1)
        data2 = trades2.get(layout, filters2)
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
    data = trades.get(layout, {})
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
def order_update_view(request):
    order_serializer = OrderSerializer(data = request.data['order'])
    if order_serializer.is_valid():
        order = order_serializer.data
        orders = Orders(request.user)
        result = orders.update(order)
        if result:
            return Response({'code': success.OK}, status=status.HTTP_200_OK)
        return Response({'code': ERROR.TRADE_UPDATE_FAILED}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def import_trades_view(request):
    serializer = ImportTradesSerializer(data = request.data)
    user = request.user
    if serializer.is_valid():
        brocker_id = serializer.data['brocker']
        portfolio_id = serializer.data['portfolio']
        brocker = Brocker.objects.get(id = brocker_id)
        portfolio = Portfolio.objects.get(id = portfolio_id)
        
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
        trade = TradeHistory(
            user=request.user,
            merged_trades=merged_filename, 
            output_trades=output_filename, 
            brocker=brocker, 
            portfolio = portfolio,
            no_trades = len(output_trades), 
            no_executions = len(merged_trades))
        trade.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def manual_trade_view(request):
    manual_trade_serialiser = ManualTradeSerializer(data = request.data)
    if manual_trade_serialiser.is_valid():
        user = request.user
        data = manual_trade_serialiser.data
        portfolio_id = data.pop('portfolio')
        portfolio = Portfolio.objects.get(user = user, pk = portfolio_id)
        trade_history = portfolio.tradehistory_set.filter(type=2)
        if not trade_history.exists():
            output_trades = pd.DataFrame()
            merged_trades = pd.DataFrame()
            filename = hashlib.md5(('manual:'+user.username).encode()).hexdigest()+'.csv'
            merged_filename = os.path.join(settings.MERGED_TRADES_PATH, filename)
            output_filename = os.path.join(settings.OUTPUT_TRADES_PATH, filename)
        else:
            merged_filename  = trade_history[0].merged_trades
            output_filename  =  trade_history[0].output_trades
            merged_trades = pd.read_csv(merged_filename)
            output_trades = pd.read_csv(output_filename)
        output_trades_list = []
        merged_trades_list = []

        sum_entry_price = 0
        sum_exit_price = 0
        entry_quantity = 0
        exit_quantity = 0
        entryTime = '99:99:99'
        entryDate = '99-99-9999'
        exitTime = '00:00:00'
        exitDate = '00-00-0000'
        no_orders = 0
        for order in data['entries']:
            no_orders +=1
            order['price'] = float(order['price'])
            sum_entry_price += order['price'] * order['volume']
            entry_quantity += order['volume']
            if order['date']<entryDate :
                entryDate = order['date']
                entryTime = order['time']
            elif order['date'] == entryDate and order['time']<entryTime:
                entryTime = order['time']
        
        for order in data['exits']:
            no_orders +=1
            order['price'] = float(order['price'])
            sum_exit_price += order['price'] * order['volume']
            exit_quantity += order['volume']
            if order['date']>exitDate :
                exitDate = order['date']
                exitTime = order['time']
            elif order['date'] == exitDate and order['time']>exitTime:
                exitTime = order['time']

        output_trade = {
            'symbol': data['symbol'],
            'exchange': '',
            'quantity': (entry_quantity+exit_quantity)/2,
            'strikePrice': '',
            'expiryDate': '',
            'optionsType': '',
            'tradeType': data['entryType'],
            'assetType': data['assetType'],
            'entryPrice': round(sum_entry_price/entry_quantity, 2),
            'entryDate': entryDate,
            'entryTime': entryTime,
            'exitPrice': round(sum_exit_price/exit_quantity, 2),
            'exitDate': exitDate,
            'exitTime': exitTime,
            'breakeven': '',
            'avgBuyPrice': round(sum_entry_price/entry_quantity, 2),
            'avgSellPrice': round(sum_exit_price/exit_quantity, 2),
            'isOpen': 1 if entry_quantity == exit_quantity else 0,
            'stoploss': data.get('stoploss', ''),
            'target': data.get('target', ''),
            'note': '',
            'setup': '',
            'mistakes': '',
            'tags': '',
            }
        output_trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), output_trade.values())).encode()).hexdigest()
        output_trades_list.append(output_trade)
        
        for order in data['entries']:
            merged_trade = {
                'symbol': data['symbol'],
                'tradeDate': order['date'],
                'exchange': '',
                'quantity': order['volume'],
                'price': order['price'],
                'executionTime': order['time'],
                'strikePrice': '',
                'expiryDate': '',
                'optionsType': '',
                'tradeType': data['entryType'],
                'assetType': data['assetType'],
                'tradeId': output_trade['id'],
            }
            merged_trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), merged_trade.values())).encode()).hexdigest()
            merged_trades_list.append(merged_trade)
        for order in data['exits']:
            merged_trade = {
                'symbol': data['symbol'],
                'tradeDate': order['date'],
                'exchange': '',
                'quantity': order['volume'],
                'price': -order['price'],
                'executionTime': order['time'],
                'strikePrice': '',
                'expiryDate': '',
                'optionsType': '',
                'tradeType': data['entryType'],
                'assetType': data['assetType'],
                'tradeId': output_trade['id'],
            }
            merged_trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), merged_trade.values())).encode()).hexdigest()
            merged_trades_list.append(merged_trade)

        if not trade_history.exists():  

            trade_history = TradeHistory(
                    user = user,
                    type = 2,
                    merged_trades = merged_filename,
                    output_trades = output_filename,
                    portfolio = portfolio,
                    no_trades = 1,
                    no_executions = no_orders
                )
            trade_history.save()
        else:
            trade_history.update(
                no_trades = trade_history[0].no_trades + 1, 
                no_executions = trade_history[0].no_executions + no_orders
            )
    
        print(output_trades)
        print(output_trades_list)
        output_trades = pd.concat([output_trades, pd.DataFrame(output_trades_list)])
        merged_trades = pd.concat([merged_trades, pd.DataFrame(merged_trades_list)])
        merged_trades.to_csv(merged_filename, index=False)
        output_trades.to_csv(output_filename, index=False)
        return Response({'code': success.OK}, status=status.HTTP_200_OK)
    return Response(manual_trade_serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# def manual_execution_view(request):
#     manual_execution_serialiser = ManualExecutionSerializer(data = request.data)
#     if manual_execution_serialiser.is_valid():
#         user = request.user
#         data = manual_execution_serialiser.data
#         portfolio_id = data.pop('portfolio')
#         portfolio = Portfolio.objects.get(user = user, pk = portfolio_id)
#         trade_history = portfolio.tradehistory_set.filter(type=2)
#         if not trade_history.exists():
#             output_trades = pd.DataFrame()
#             merged_trades = pd.DataFrame()
#             filename = hashlib.md5(('manual:'+user.username).encode()).hexdigest()+'.csv'
#             merged_filename = os.path.join(settings.MERGED_TRADES_PATH, filename)
#             output_filename = os.path.join(settings.OUTPUT_TRADES_PATH, filename)
#         else:
#             merged_filename  = trade_history[0].merged_trades
#             output_filename  =  trade_history[0].output_trades
#             merged_trades = pd.read_csv(merged_filename)
#             output_trades = pd.read_csv(output_filename)
#         output_trades_list = []
#         merged_trades_list = []

#         sum_entry_price = 0
#         sum_exit_price = 0
#         entry_quantity = 0
#         exit_quantity = 0
#         entryTime = '99:99:99'
#         entryDate = '99-99-9999'
#         exitTime = '00:00:00'
#         exitDate = '00-00-0000'
#         no_orders = 0
#         for order in data['entries']:
#             no_orders +=1
#             order['price'] = float(order['price'])
#             sum_entry_price += order['price'] * order['volume']
#             entry_quantity += order['volume']
#             if order['date']<entryDate :
#                 entryDate = order['date']
#                 entryTime = order['time']
#             elif order['date'] == entryDate and order['time']<entryTime:
#                 entryTime = order['time']
        
#         for order in data['exits']:
#             no_orders +=1
#             order['price'] = float(order['price'])
#             sum_exit_price += order['price'] * order['volume']
#             exit_quantity += order['volume']
#             if order['date']>exitDate :
#                 exitDate = order['date']
#                 exitTime = order['time']
#             elif order['date'] == exitDate and order['time']>exitTime:
#                 exitTime = order['time']

#         output_trade = {
#             'symbol': data['symbol'],
#             'exchange': '',
#             'quantity': (entry_quantity+exit_quantity)/2,
#             'strikePrice': '',
#             'expiryDate': '',
#             'optionsType': '',
#             'tradeType': data['entryType'],
#             'assetType': data['assetType'],
#             'entryPrice': round(sum_entry_price/entry_quantity, 2),
#             'entryDate': entryDate,
#             'entryTime': entryTime,
#             'exitPrice': round(sum_exit_price/exit_quantity, 2),
#             'exitDate': exitDate,
#             'exitTime': exitTime,
#             'breakeven': '',
#             'avgBuyPrice': round(sum_entry_price/entry_quantity, 2),
#             'avgSellPrice': round(sum_exit_price/exit_quantity, 2),
#             'isOpen': 1 if entry_quantity == exit_quantity else 0,
#             'stoploss': data.get('stoploss', ''),
#             'target': data.get('target', ''),
#             'note': '',
#             'setup': '',
#             'mistakes': '',
#             'tags': '',
#             }
#         output_trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), output_trade.values())).encode()).hexdigest()
#         output_trades_list.append(output_trade)
        
#         for order in data['entries']:
#             merged_trade = {
#                 'symbol': data['symbol'],
#                 'tradeDate': order['date'],
#                 'exchange': '',
#                 'quantity': order['volume'],
#                 'price': order['price'],
#                 'executionTime': order['time'],
#                 'strikePrice': '',
#                 'expiryDate': '',
#                 'optionsType': '',
#                 'tradeType': data['entryType'],
#                 'assetType': data['assetType'],
#                 'tradeId': output_trade['id'],
#             }
#             merged_trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), merged_trade.values())).encode()).hexdigest()
#             merged_trades_list.append(merged_trade)
#         for order in data['exits']:
#             merged_trade = {
#                 'symbol': data['symbol'],
#                 'tradeDate': order['date'],
#                 'exchange': '',
#                 'quantity': order['volume'],
#                 'price': -order['price'],
#                 'executionTime': order['time'],
#                 'strikePrice': '',
#                 'expiryDate': '',
#                 'optionsType': '',
#                 'tradeType': data['entryType'],
#                 'assetType': data['assetType'],
#                 'tradeId': output_trade['id'],
#             }
#             merged_trade['id'] = hashlib.md5(':'.join(map(lambda i: str(i), merged_trade.values())).encode()).hexdigest()
#             merged_trades_list.append(merged_trade)

#         if not trade_history.exists():  

#             trade_history = TradeHistory(
#                     user = user,
#                     type = 2,
#                     merged_trades = merged_filename,
#                     output_trades = output_filename,
#                     portfolio = portfolio,
#                     no_trades = 1,
#                     no_executions = no_orders
#                 )
#             trade_history.save()
#         else:
#             trade_history.update(
#                 no_trades = trade_history[0].no_trades + 1, 
#                 no_executions = trade_history[0].no_executions + no_orders
#             )
    
#         print(output_trades)
#         print(output_trades_list)
#         output_trades = pd.concat([output_trades, pd.DataFrame(output_trades_list)])
#         merged_trades = pd.concat([merged_trades, pd.DataFrame(merged_trades_list)])
#         merged_trades.to_csv(merged_filename, index=False)
#         output_trades.to_csv(output_filename, index=False)
#         return Response({'code': success.OK}, status=status.HTTP_200_OK)
#     return Response(manual_trade_serialiser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def symbols_view(request):
    trades = Trades(request.user)
    data = trades.get([fields.symbols()], {})['symbols']
    return Response(data, status=status.HTTP_200_OK)

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def edit_portfolio_view(request):
    pk = request.data.pop('pk')
    print(pk)
    portfolios = Portfolio.objects.filter(user = request.user, pk = pk)
    if portfolios.exists():
        portfolios.update(**request.data)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def portfolio_view(request):
    portfolios = Portfolio.objects.filter(user = request.user)
    if portfolios.exists():
        serializer = PortfolioSeriliser(portfolios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_portfolio_view(request):
    serializer = PortfolioSeriliser(data=request.data)
    if serializer.is_valid():
        serializer.save(user = request.user)
        return Response(status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_portfolio_view(request):
    portfolios = Portfolio.objects.filter(user = request.user, pk = request.data['pk'])
    if portfolios.exists():
        portfolios.delete()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_adjustment_view(request):
    portfolio_entry_serializer = PortfolioEntrySeriliser(data = request.data)
    if portfolio_entry_serializer.is_valid():
        portfolio_entry_serializer.save()
        return Response(status=status.HTTP_200_OK)
    return Response(data = portfolio_entry_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
