import pandas as pd
import os
import uuid
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .utils import MergedTrades, Rule, CheckRule, OutputTrades, uniqueTrades
from .serializers import BrockerNamesSerializer, BrockerSerializer, UploadTradesSerializer, FilterSerializer, OutputTradesSerializer
from .models import Brocker, Trade
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def uploadTradesView(request):
    serializer = UploadTradesSerializer(data = request.data, context={'request': request})
    if serializer.is_valid():
        try:
            brocker_id = serializer.data['brocker']
            brocker = Brocker.objects.get(id = brocker_id)
            
            file = serializer.validated_data['file']
            filename = uuid.uuid4().hex+'.csv'
            merged_filename = os.path.join(settings.MERGED_TRADES_PATH, filename)
            output_filename = os.path.join(settings.OUTPUT_TRADES_PATH, filename)

            fields_rule = Rule(brocker.fields_rule)
            assets_rule = CheckRule('assets_type', brocker.assets_rule)
            options_rule = CheckRule('options_type', brocker.options_rule)
            
            mt = MergedTrades(file)
            mt.addRule(fields_rule)
            mt.addRule(assets_rule)
            mt.addRule(options_rule)
            mTradeDf = mt.save(merged_filename)

            ot = OutputTrades(mTradeDf)
            ot.save(output_filename)
            
            trade = Trade(user=request.user, merged_trades=merged_filename, output_trades=output_filename, brocker=brocker)
            trade.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response({'message': 'Internal error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def outputTradesView(request):
    user = request.user
    trades = Trade.objects.filter(user = user)
    fSerializer = FilterSerializer(data = request.data)
    if fSerializer.is_valid():
        filters = fSerializer.data
        trades = uniqueTrades(trades)
        if filters['symbols']:
            trades = trades.loc[trades['symbol'].isin(filters['symbols'])]
        trades = trades[filters['start']:filters['start']+filters['limit']]
        list_trades = []
        for i, trade in trades.iterrows():
            list_trades.append(trade.to_dict())
        outputTradesSerializer = OutputTradesSerializer(data=list_trades, many=True)
        if outputTradesSerializer.is_valid():
            return Response(outputTradesSerializer.data, status=status.HTTP_200_OK)
        return Response(outputTradesSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(fSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def filtersView(request):
    user = request.user
    trades = Trade.objects.filter(user = user)
    trades = uniqueTrades(trades)
    filters = {}
    symbols = trades['symbol'].drop_duplicates()
    filters['symbols'] = symbols
    serializer = FilterSerializer(data = filters)
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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