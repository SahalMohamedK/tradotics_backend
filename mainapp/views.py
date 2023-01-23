import pandas as pd
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .utils import TradeHandler, Rule, CheckRule
from .serializers import BrockerNamesSerializer, BrockerSerializer, ImportTradesSerializer, TradesSerializer
from .models import Brocker, Trade, MergedTrade
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def importTradesView(request):
    serializer = ImportTradesSerializer(data = request.data, context={'request': request})
    if serializer.is_valid():
        importTrade = serializer.save(user=request.user)
        filename = importTrade.file.path
        brocker = importTrade.brocker
        fields_rule = Rule(brocker.fields_rule)
        assets_rule = CheckRule('assets_type', brocker.assets_rule)
        options_rule = CheckRule('options_type', brocker.options_rule)
        th = TradeHandler(filename)
        th.addRule(fields_rule)
        th.addRule(assets_rule)
        th.addRule(options_rule)
        trades = th.convert()
        df = pd.DataFrame(trades)
        df.to_csv(settings.MEDIA_ROOT+'/merged_trades/'+str(request.user.id)+'.csv')
        # try:
        # except:
        #     return Response({'message': 'Internal error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def tradesView(request):
    user = request.user
    trades = Trade.objects.filter(user = user)
    
    serializer = TradesSerializer(trades, many = True)
    return Response(serializer.data, status=status.HTTP_200_OK)

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