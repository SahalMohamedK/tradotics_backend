from rest_framework import serializers
import os
from .models import Brocker, TradeHistory
from django.core.validators import FileExtensionValidator
from .consts import SUPPORTED_FILE_TYPES

class ImportTradesSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=SUPPORTED_FILE_TYPES)])
    brocker = serializers.IntegerField()

class FiltersQuarySerializer(serializers.Serializer):
    symbol = serializers.ListField(child = serializers.CharField(), default=[], required = False)
    side = serializers.ListField(child = serializers.CharField(), default = [], required = False)
    price = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    # setup = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    status = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    asset_type = serializers.ListField(child = serializers.CharField(), default = [], required = False)
    duration = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    day = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    call_put = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    hour = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    r_mutiple = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    notes_filled = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)

class TradeTableQuerySerializer(serializers.Serializer):
    filters = FiltersQuarySerializer()
    start = serializers.IntegerField()
    size = serializers.IntegerField()

class FiltersSerializer(serializers.Serializer):
    symbol = serializers.ListField()
    side = serializers.ListField()
    price = serializers.ListField()
    # setup = serializers.ListField()
    status = serializers.ListField()
    asset_type = serializers.ListField()
    duration = serializers.ListField()
    day = serializers.ListField()
    call_put = serializers.ListField()
    hour = serializers.ListField()
    r_mutiple = serializers.ListField()
    notes_filled = serializers.ListField()

class TradeSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    entryDate = serializers.DateField()
    symbol = serializers.CharField()
    netPnl = serializers.DecimalField(max_digits=30, decimal_places=2)
    roi = serializers.FloatField()
    tradeType = serializers.CharField()
    quantity = serializers.IntegerField()
    entryTime = serializers.TimeField()
    exitPrice = serializers.DecimalField(max_digits=30, decimal_places=2)
    exitDate = serializers.DateField()
    exitTime = serializers.TimeField()
    entryPrice= serializers.DecimalField(max_digits=30, decimal_places=2)
    id = serializers.CharField()
    tradeHistory = serializers.IntegerField()
    stoploss = serializers.IntegerField(required = False)
    target = serializers.IntegerField(required = False)
    note = serializers.CharField()
    setup = serializers.ListField()

class OrderSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    tradeDate = serializers.DateField()
    exchange = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=30, decimal_places=15)
    executionTime = serializers.TimeField()
    # expiryDate = serializers.DateField(required = False)
    optionsType = serializers.CharField()
    tradeType = serializers.CharField()
    assetType = serializers.CharField()
    id = serializers.CharField()

class TradeAnalyticsSerializer(serializers.Serializer):
    trade = TradeSerializer()
    orders = OrderSerializer(many = True)
    duration = serializers.CharField()

class TradesTableSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    entryDate = serializers.DateField()
    symbol = serializers.CharField()
    netPnl = serializers.DecimalField(max_digits=30, decimal_places=15)
    roi = serializers.FloatField()
    tradeType = serializers.CharField()
    quantity = serializers.IntegerField()
    entryTime = serializers.TimeField()
    exitPrice = serializers.DecimalField(max_digits=30, decimal_places=15)
    exitDate = serializers.DateField()
    exitTime = serializers.TimeField()
    entryPrice= serializers.DecimalField(max_digits=30, decimal_places=15)
    id = serializers.CharField()

class DashboradSerializer(serializers.Serializer):
    isDemo = serializers.BooleanField()
    tradesTable = TradesTableSerializer(many = True)
    openTrades = TradesTableSerializer(many=True)
    cumulativePnl = serializers.ListField()
    totalNetPnl = serializers.FloatField()
    totalTrades = serializers.IntegerField()
    totalProfitFactor = serializers.FloatField()
    tradesByDays = serializers.DictField()
    winners = serializers.IntegerField()
    losers = serializers.IntegerField()
    winnersByDays = serializers.IntegerField()
    losersByDays = serializers.IntegerField()
    returns = serializers.DictField()
    insights = serializers.ListField()
    pnlByDays = serializers.ListField()
    pnlByMonths = serializers.ListField()
    pnlBySetup = serializers.ListField()
    pnlByDuration = serializers.ListField()
    dialyPnl = serializers.ListField()

class DetailsReportSerializer(serializers.Serializer):
    winners = serializers.IntegerField()
    losers = serializers.IntegerField()
    totalTrades = serializers.IntegerField()
    returns = serializers.DictField()
    totalQuantity = serializers.IntegerField()
    days = serializers.DictField()
    maxConsec = serializers.ListField()
    counts = serializers.DictField()
    rois = serializers.DictField()
    openAndClose = serializers.ListField()
    highestPnl = TradesTableSerializer()
    lowestPnl = TradesTableSerializer()
    holdTimes = serializers.ListField()
    dateToExpiry = serializers.ListField()
    dayDistribution = serializers.ListField()
    hourDistribution = serializers.ListField()
    setupDistribution = serializers.ListField()
    durationDistribution = serializers.ListField()
    costDistribution = serializers.ListField()
    priceDistribution = serializers.ListField()
    symbolDistribution = serializers.ListField()

class TradesSerializer(serializers.Serializer):
    trades_table = TradesTableSerializer(many = True)
    winners = serializers.IntegerField()
    losers = serializers.IntegerField()
    total_trades = serializers.IntegerField()
    highestPnl = TradesTableSerializer()
    lowestPnl = TradesTableSerializer()

class CalenderSerializer(serializers.Serializer):
    tradesByDays = serializers.DictField()

class CompareTradesSerializer(serializers.Serializer):
    cumulativePnl = serializers.ListField()
    winners = serializers.IntegerField()
    lossers = serializers.IntegerField()
    highestPnl = serializers.FloatField()
    lowestPnl = serializers.FloatField()
    profitFactor = serializers.FloatField()
    returns = serializers.DictField()
    holdTimes = serializers.ListField()
    totalTrades = serializers.IntegerField()

class CompareSerializer(serializers.Serializer):
    trades1 = CompareTradesSerializer()
    trades2 = CompareTradesSerializer()
    doubleCumulativePnl = serializers.ListField()
    doubleDialyPnl = serializers.ListField()
    pnlByDays = serializers.ListField()
    pnlByMonths = serializers.ListField()
    pnlByDuration = serializers.ListField()    

class BrockerNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brocker
        fields = ['name', 'pk']

class BrockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brocker
        fields = ['name', 'desc']

class TradeHistrotySerializer(serializers.ModelSerializer):
    brocker = BrockerNamesSerializer()
    class Meta:
        model = TradeHistory
        fields = ('brocker', 'type', 'created', 'no_trades', 'no_executions', 'pk')