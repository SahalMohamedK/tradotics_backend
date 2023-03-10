from rest_framework import serializers
import os
from .models import Brocker, TradeHistory, Comparison, Portfolio, PortfolioEntry
from django.core.validators import FileExtensionValidator
from .consts import SUPPORTED_FILE_TYPES

class ImportTradesSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=SUPPORTED_FILE_TYPES)])
    brocker = serializers.IntegerField()
    portfolio = serializers.IntegerField()

class ManualTradeOrderSeriaiser(serializers.Serializer):
    date = serializers.DateField()
    time = serializers.TimeField()
    volume = serializers.IntegerField()
    price = serializers.DecimalField(max_digits= 12,decimal_places=2)

class ManualTradeSerializer(serializers.Serializer):
    assetType = serializers.IntegerField()
    symbol = serializers.CharField()
    entryType = serializers.IntegerField()
    entries = serializers.ListField(child=ManualTradeOrderSeriaiser(), allow_empty=False)
    exits = serializers.ListField(child=ManualTradeOrderSeriaiser(), allow_empty=False)
    stoploss = serializers.FloatField(required = False)
    target = serializers.FloatField(required = False)
    portfolio = serializers.IntegerField()

class ManualExecutionSerializer(serializers.Serializer):
    assetType = serializers.IntegerField()
    symbol = serializers.CharField()
    entryType = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()
    volume = serializers.IntegerField()
    price = serializers.DecimalField(max_digits= 12,decimal_places=2)
    portfolio = serializers.IntegerField()

class FiltersQuarySerializer(serializers.Serializer):
    symbol = serializers.ListField(child = serializers.CharField(), default=[], required = False)
    side = serializers.ListField(child = serializers.CharField(), default = [], required = False)
    price = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    setup = serializers.ListField(child = serializers.CharField(), default = [], required = False)
    mistakes = serializers.ListField(child = serializers.CharField(), default = [], required = False)
    tags = serializers.ListField(child = serializers.CharField(), default = [], required = False)
    status = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    assetType = serializers.ListField(child = serializers.CharField(), default = [], required = False)
    duration = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    day = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    optionsType = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    hour = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    # r_mutiple = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    notesFilled = serializers.ListField(child = serializers.IntegerField(), default = [], required = False)
    fromDate = serializers.DateField(format='%Y-%m-%d', required = False)
    toDate = serializers.DateField(format='%Y-%m-%d', required = False)

class PaginationQuarySerializer(serializers.Serializer):
    filters = FiltersQuarySerializer()
    start = serializers.IntegerField()
    size = serializers.IntegerField()

class TradeTableQuerySerializer(serializers.Serializer):
    filters = FiltersQuarySerializer()
    start = serializers.IntegerField()
    size = serializers.IntegerField()

class FiltersSerializer(serializers.Serializer):
    symbol = serializers.ListField()
    side = serializers.ListField()
    price = serializers.ListField()
    setup = serializers.ListField()
    mistakes = serializers.ListField()
    tags = serializers.ListField()
    status = serializers.ListField()
    asset_type = serializers.ListField()
    duration = serializers.ListField()
    day = serializers.ListField()
    call_put = serializers.ListField()
    hour = serializers.ListField()
    r_mutiple = serializers.ListField()
    notes_filled = serializers.ListField()

class CompareQuerySerializer(serializers.Serializer):
    filters1 = FiltersQuarySerializer()
    filters2 = FiltersQuarySerializer()

class ComparisonSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Comparison
        fields = ('filters1', 'filters2', 'name', 'desc', 'group1', 'group2', 'is_popular')
        extra_kwargs = {
            'is_popular': {
                'read_only': True,
            },
            'filters1': {
                'required': True, 
            },
            'filters2': {
                'required': True, 
            }
        }

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
    note = serializers.CharField(allow_blank=True)
    setup = serializers.ListField()
    mistakes = serializers.ListField()
    tags = serializers.ListField()

class OrderSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    tradeDate = serializers.DateField()
    tradeHistory = serializers.IntegerField()
    exchange = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=30, decimal_places=15)
    executionTime = serializers.TimeField()
    expiryDate = serializers.DateField(read_only = True)
    optionsType = serializers.CharField(read_only = True)
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

class PortfolioEntrySeriliser(serializers.ModelSerializer):
    class Meta:
        model = PortfolioEntry
        fields = '__all__'

class PortfolioSeriliser(serializers.ModelSerializer):
    portfolioentry_set = PortfolioEntrySeriliser(many = True, read_only=True)
    class Meta:
        model = Portfolio
        fields = ('name', 'portfolioentry_set', 'pk')

class TradeHistrotySerializer(serializers.ModelSerializer):
    brocker = BrockerNamesSerializer()
    portfolio = PortfolioSeriliser()
    class Meta:
        model = TradeHistory
        fields = ('brocker', 'portfolio', 'type', 'created', 'no_trades', 'no_executions', 'pk')


