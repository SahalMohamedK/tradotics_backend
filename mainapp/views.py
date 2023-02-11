import pandas as pd
import os
import hashlib
import datetime
from io import StringIO
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .trades import MergedTrades, OutputTrades, Trades, DemoTrades
from .serializers import BrockerNamesSerializer, BrockerSerializer, ImportTradesSerializer, FiltersQuarySerializer, \
    DashboradSerializer, DetailsReportSerializer, TradesSerializer, TradeAnalyticsSerializer, FiltersSerializer, \
    CalenderSerializer, CompareSerializer, TradeHistrotySerializer, TradeSerializer, TradeTableQuerySerializer, \
    TradesTableSerializer
from .models import Brocker, TradeHistory
from django.conf import settings
from .utils import human_delta
from .consts import ERROR

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trades_table_view(request):
    user = request.user
    trade_table_query_serializer = TradeTableQuerySerializer(data = request.data)
    if trade_table_query_serializer.is_valid():
        filters = trade_table_query_serializer.data['filters']
        start = trade_table_query_serializer.data['start']
        size = trade_table_query_serializer.data['size']
        trades = Trades(user)
        trades.filters.apply(filters)
        trades = trades.get()[start:start+size]
        trades_table_serializer = TradesTableSerializer(data = trades, many = True)
        if trades_table_serializer.is_valid():
            return Response(trades_table_serializer.data, status=status.HTTP_200_OK)
        return Response(trades_table_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(trade_table_query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def dashboard_view(request):
    user = request.user
    filter_serializer = FiltersQuarySerializer(data = request.data)
    if filter_serializer.is_valid():
        filters = filter_serializer.data
        trades = Trades(user)
        trades.filters.apply(filters)
        winners, losers = trades.winners_and_losers()
        winners_by_days, losers_by_days = trades.winners_and_losers_by_days()
        dashboard_data = {
            'isDemo': trades.is_demo,
            'tradesTable': trades.get()[: 25],
            'cumulativePnl': trades.cumulative_pnl(),
            'totalNetPnl' : trades.total_net_pnl(),
            'totalTrades' : trades.total_trades(),
            'totalProfitFactor' : trades.profit_factor(),
            'tradesByDays': trades.get_trades_by_days(),
            'winners': winners,
            'losers': losers,
            'returns': trades.returns(),
            'winnersByDays':winners_by_days,
            'losersByDays': losers_by_days,
            'insights': trades.dashboard_insights(),
            'openTrades': trades.open_trades(),
            'pnlByDays': trades.pnl_by_days()[0],
            'pnlByMonths': trades.pnl_by_months()[0],
            'pnlBySetup': trades.pnl_by_setup()[0],
            'pnlByDuration': trades.pnl_by_duration()[0],
            'dialyPnl': trades.dialy_pnl()
        }
        dashboradSerializer = DashboradSerializer(data=dashboard_data)
        if dashboradSerializer.is_valid():
            return Response(dashboradSerializer.data, status=status.HTTP_200_OK)
        return Response(dashboradSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
        winners, losers = trades.winners_and_losers()
        highestPnl, lowestPnl = trades.highest_and_lowest_pnl()
        detailed_report_data = {
            'winners': winners,
            'losers': losers,
            'totalTrades' : trades.total_trades(),
            'returns': trades.returns(),
            'totalQuantity': trades.total_quantity(),
            'days': trades.days(),
            'maxConsec': trades.max_consec(),
            'counts': trades.counts(),
            'rois': trades.rois(),
            'openAndClose': trades.open_and_close(),
            'highestPnl': highestPnl,
            'lowestPnl': lowestPnl,
            'holdTimes': trades.hold_times(),
            'dateToExpiry': trades.date_to_expiry(),
            'dayDistribution': trades.pnl_by_days(),
            'hourDistribution': trades.pnl_by_hours(),
            'setupDistribution': trades.pnl_by_setup(),
            'durationDistribution': trades.pnl_by_duration(),
            'costDistribution': trades.pnl_by_cost(),
            'priceDistribution': trades.pnl_by_price(),
            'symbolDistribution': trades.pnl_by_symbol()
        }
        trades.pnl_by_cost()
        detailed_report_serializer = DetailsReportSerializer(data=detailed_report_data)
        if detailed_report_serializer.is_valid():
            return Response(detailed_report_serializer.data, status=status.HTTP_200_OK)
        return Response(detailed_report_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trades_view(request):
    user = request.user
    filter_serializer = FiltersQuarySerializer(data = request.data)
    if filter_serializer.is_valid():
        filters = filter_serializer.data
        trades = Trades(user)
        trades.apply_filter(filters)
        highestPnl, lowestPnl = trades.highest_and_lowest_pnl()
        winners, losers = trades.winners_and_losers()
        detailed_report_data = {
            'trades_table': trades.get()[:25],
            'winners': winners,
            'losers': losers,
            'highestPnl': highestPnl,
            'lowestPnl': lowestPnl,
            'total_trades' : trades.total_trades()
        }
        trades_serializer = TradesSerializer(data=detailed_report_data)
        if trades_serializer.is_valid():
            return Response(trades_serializer.data, status=status.HTTP_200_OK)
        return Response(trades_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def calender_views(request):
    user = request.user
    filter_serializer = FiltersQuarySerializer(data = request.data)
    if filter_serializer.is_valid():
        filters = filter_serializer.data
        trades = Trades(user)
        trades.filters.apply(filters)
        calender_views_data = {
            'tradesByDays': trades.get_trades_by_days(),
        }
        calender_serializer = CalenderSerializer(data=calender_views_data)
        if calender_serializer.is_valid():
            return Response(calender_serializer.data, status=status.HTTP_200_OK)
        return Response(calender_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def compare_views(request):
    user = request.user
    filter_1 = request.data['filter1']
    filter_2 = request.data['filter2']
    filter_serializer_1 = FiltersQuarySerializer(data = filter_1)
    filter_serializer_2 = FiltersQuarySerializer(data = filter_2)
    if filter_serializer_1.is_valid():
        if filter_serializer_2.is_valid():
            filters_1 = filter_serializer_1.data
            filters_2 = filter_serializer_2.data
            trades_1 = Trades(user)
            trades_2 = Trades(user)
            trades_1.filters.apply(filters_1)
            trades_2.filters.apply(filters_2)
        
            winners_1, losers_1 = trades_1.winners_and_losers()
            winners_2, losers_2 = trades_2.winners_and_losers()

            highest_pnl_1, lowest_pnl_1 = trades_1.highest_and_lowest_pnl()
            highest_pnl_2, lowest_pnl_2 = trades_2.highest_and_lowest_pnl()

            cumulativePnl1 = trades_1.cumulative_pnl()
            cumulativePnl2 = trades_2.cumulative_pnl()
            doubleCumulativeLabels = cumulativePnl1[0]+cumulativePnl2[0]
            doubleCumulativeLabels = list(set(doubleCumulativeLabels))
            doubleCumulativeLabels.sort(key = lambda i: datetime.datetime.strptime(i, '%Y-%m-%d'))
            doubleCumulativePnls1 = []
            doubleCumulativePnls2 = []
            prevPnl1 = 0
            prevPnl2 = 0
            for label in doubleCumulativeLabels:
                if doubleCumulativePnls1:
                    prevPnl1 = doubleCumulativePnls1[-1]
                if doubleCumulativePnls2:
                    prevPnl2 = doubleCumulativePnls2[-1]  
                if label in cumulativePnl1[0] and label in cumulativePnl2[0]:
                    doubleCumulativePnls1.append(cumulativePnl1[1][cumulativePnl1[0].index(label)])                   
                    doubleCumulativePnls2.append(cumulativePnl2[1][cumulativePnl2[0].index(label)])
                elif label in cumulativePnl1[0]:               
                    doubleCumulativePnls1.append(cumulativePnl1[1][cumulativePnl1[0].index(label)])
                    doubleCumulativePnls2.append(prevPnl2)
                elif label in cumulativePnl2[0]:
                    doubleCumulativePnls2.append(cumulativePnl2[1][cumulativePnl2[0].index(label)])                 
                    doubleCumulativePnls1.append(prevPnl1)

            dialy_pnl1 = trades_1.dialy_pnl()
            dialy_pnl2 = trades_2.dialy_pnl()
            double_dialy_labels = dialy_pnl1[0]+dialy_pnl2[0]
            double_dialy_labels = list(set(double_dialy_labels))
            double_dialy_labels.sort(key = lambda i: datetime.datetime.strptime(i, '%Y-%m-%d'))
            double_dialy_pnls1 = []
            double_dialy_pnls2 = []
            for label in double_dialy_labels:
                if label in dialy_pnl1[0] and label in dialy_pnl2[0]:
                    double_dialy_pnls1.append(dialy_pnl1[1][dialy_pnl1[0].index(label)])                   
                    double_dialy_pnls2.append(dialy_pnl2[1][dialy_pnl2[0].index(label)])
                elif label in dialy_pnl1[0]:               
                    double_dialy_pnls1.append(dialy_pnl1[1][dialy_pnl1[0].index(label)])
                    double_dialy_pnls2.append(0)
                elif label in dialy_pnl2[0]:
                    double_dialy_pnls2.append(dialy_pnl2[1][dialy_pnl2[0].index(label)])                 
                    double_dialy_pnls1.append(0)

            pnl_by_days1 = trades_1.pnl_by_days()[0]
            pnl_by_days2 = trades_2.pnl_by_days()[0]

            pnl_by_months1 = trades_1.pnl_by_months()[0]
            pnl_by_months2 = trades_2.pnl_by_months()[0]

            pnl_by_duration1 = trades_1.pnl_by_duration()[0]
            pnl_by_duration2 = trades_2.pnl_by_duration()[0]

            compare_data = {
                'trades1': {
                    'cumulativePnl': cumulativePnl1,
                    'winners': winners_1,
                    'lossers': losers_1,
                    'totalTrades' : trades_1.total_trades(),        
                    'highestPnl': highest_pnl_1['netPnl'],
                    'lowestPnl': lowest_pnl_1['netPnl'],
                    'profitFactor': trades_1.profit_factor(),
                    'returns': trades_1.returns(),
                    'holdTimes': trades_1.hold_times(),
                },
                'trades2': {
                    'cumulativePnl': cumulativePnl2,
                    'winners': winners_2,
                    'lossers': losers_2,
                    'totalTrades' : trades_2.total_trades(),        
                    'highestPnl': highest_pnl_2['netPnl'],
                    'lowestPnl': lowest_pnl_2['netPnl'],
                    'profitFactor': trades_2.profit_factor(),
                    'returns': trades_2.returns(),
                    'holdTimes': trades_2.hold_times(),
                },
                'doubleCumulativePnl': [doubleCumulativeLabels, doubleCumulativePnls1, doubleCumulativePnls2],
                'doubleDialyPnl': [double_dialy_labels, double_dialy_pnls1, double_dialy_pnls2],
                'pnlByDays': [pnl_by_days1, pnl_by_days2],
                'pnlByMonths': [pnl_by_months1, pnl_by_months2],
                'pnlByDuration': [pnl_by_duration1, pnl_by_duration2]
            }
            compare_serializer = CompareSerializer(data = compare_data)
            if compare_serializer.is_valid():
                return Response(compare_serializer.data, status=status.HTTP_200_OK)
            return Response(compare_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'filter2': filter_serializer_2.errors}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'filter1': filter_serializer_1.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trade_view(request, id):
    user = request.user
    trade_histories = TradeHistory.objects.filter(user = user)
    trades = Trades(user)
    if trade_histories.exists():
        merged_trades = pd.DataFrame()
        is_merged_trades = False
        for trade_history in trade_histories:
            merged_filename = trade_history.merged_trades
            merged_trade = pd.read_csv(merged_filename)
            if is_merged_trades:
                merged_trades = pd.concat([merged_trades, merged_trade]).drop_duplicates()
            else:
                is_merged_trades = True
                merged_trades = merged_trade
    if not merged_trades.empty:
        orders = merged_trades[merged_trades['tradeId'] == id]
        if not orders.empty:
            orders = orders.to_dict('records')
        else:
            orders = []

        trade = trades.get(id)
        if trade:
            entry = datetime.datetime.strptime(f"{trade['entryDate']} {trade['entryTime']}", '%Y-%m-%d %H:%M:%S')
            exit = datetime.datetime.strptime(f"{trade['exitDate']} {trade['exitTime']}", '%Y-%m-%d %H:%M:%S')
            print(trade)
            data = {
                'trade': trade,
                'orders': orders,
                'duration': human_delta(exit-entry),
            }
            trade_serializer = TradeAnalyticsSerializer(data= data)
            if trade_serializer.is_valid():
                return Response(trade_serializer.data, status=status.HTTP_200_OK)
            return Response(trade_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'code': ERROR.NO_TRADE}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'code': ERROR.NO_TRADE_HISTORIES}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def trade_update_view(request):
    user = request.user
    trade_update_serializer = TradeSerializer(data = request.data['trade'])
    if trade_update_serializer.is_valid():
        trade_update = trade_update_serializer.data
        result = False
        trade_histories = TradeHistory.objects.filter(user = user)
        for trade_history in trade_histories:
            if trade_history.pk == trade_update['tradeHistory']:
                output_trades = pd.read_csv(trade_history.output_trades)
                trade = output_trades[output_trades['id'] == trade_update['id']]
                index = trade.index[0]
                trade = trade.to_dict('records')[0]
                trade_update['setup'] = ','.join(trade_update['setup'])
                for column in trade_update:
                    if column in trade and trade[column] != trade_update[column]:
                        output_trades.loc[index, column] = trade_update[column]
                output_trades.to_csv(trade_history.output_trades, index=False)
                result = True
                break
        if result:
            return Response({'message': 'Success'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalied trade updation'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(trade_update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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