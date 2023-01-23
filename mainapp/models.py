from datetime import datetime, date
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .consts import PNL_STATUS, TRADE_TYPE, DEFUALT_FIELDS_RULE,\
    DEFUALT_ASSETS_RULE, DEFUALT_OPTIONS_RULE, OPTIONS_TYPE, ASSETS_TYPE

class Brocker(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    desc = RichTextField()

    fields_rule = models.TextField(default=DEFUALT_FIELDS_RULE)
    assets_rule = models.TextField(default=DEFUALT_ASSETS_RULE)
    options_rule = models.TextField(default=DEFUALT_OPTIONS_RULE)

    def __str__(self):
        return self.name

class ImportTrade(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="trade_uploads")
    file = models.FileField(upload_to="trade_uploads", validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    brocker = models.ForeignKey(Brocker, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.file}"

class MergedTrade(models.Model):					
    # position	
    # Realized PnL
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10, null = True)
    trade_date = models.CharField(max_length=100, null=True)
    exchange = models.CharField(max_length=10, null = True)
    segment = models.CharField(max_length=10, null = True)
    series = models.CharField(max_length=10, null = True)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE.choices, null = True)
    quantity = models.FloatField(null = True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null = True)
    order_id = models.CharField(max_length=50, null = True)
    order_execution_time = models.CharField(max_length= 100, null =True)
    strike_price = models.DecimalField(default= 0, max_digits=10, decimal_places=2, null = True)
    expiry_date = models.DateField(null = True)
    options_type = models.CharField(max_length=5, null = True, choices=OPTIONS_TYPE.choice)
    assets_type = models.CharField(max_length=20, null = True, choices=ASSETS_TYPE.choice)

    class Meta:
        ordering = ("order_execution_time",)

    def __str__(self):
        return f"{self.order_id} - {self.user}: {self.symbol} {self.trade_type} {self.quantity} @ {self.price}"

class Trade(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="trade_outputs")
    symbol = models.CharField(max_length=50)
    date = models.DateField()
    breakeven_point = models.PositiveIntegerField()
    exchange = models.CharField(max_length=10)
    segment = models.CharField(max_length=10)
    entry_time = models.TimeField()
    exit_time = models.TimeField()
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE.choices)
    quantity = models.PositiveIntegerField()
    orders = models.ManyToManyField(MergedTrade, related_name="trade")
    target = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stoploss = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    #exntry_price
    #exit_price

    @property
    def avg_sell_price(self):
        related_orders = self.orders.all()
        total_sell_price = sum(
            order.price * order.quantity for order in related_orders if order.trade_type == "sell")
        total_quantity = sum(
            order.quantity for order in related_orders if order.trade_type == "sell")
        return round(total_sell_price / total_quantity, 4)

    @property
    def avg_buy_price(self):
        related_orders = self.orders.all()
        total_buy_price = sum(
            order.price * order.quantity for order in related_orders if order.trade_type == "buy")
        total_quantity = sum(
            order.quantity for order in related_orders if order.trade_type == "buy")
        return round(total_buy_price / total_quantity, 4)

    @property
    def pnl(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return round((self.avg_sell_price - self.avg_buy_price) * self.quantity, 4)
        else:
            return round((self.avg_buy_price - self.avg_sell_price) * self.quantity, 4)

    @property
    def pnl_status(self):
        if self.pnl > 0:
            return PNL_STATUS.WIN
        elif self.pnl < 0:
            return PNL_STATUS.LOSS
        return PNL_STATUS.BREAKEVEN

    @property
    def duration(self):
        delta = datetime.combine(
            date.today(), self.exit_time) - datetime.combine(date.today(), self.entry_time)
        return delta

    @property
    def roi(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return round((self.avg_sell_price - self.avg_buy_price) / self.avg_buy_price, 4)
        return round((self.avg_buy_price - self.avg_sell_price) / self.avg_sell_price, 4)

    @property
    def planned_rr(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return round((self.target - self.avg_sell_price) / (self.avg_sell_price - self.stoploss), 4)
        return round((self.target - self.avg_sell_price) / (self.avg_sell_price - self.stoploss), 4)

    @property
    def realised_rr(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return round((self.avg_sell_price - self.avg_buy_price) / (self.avg_buy_price - self.stoploss), 4)
        return round((self.avg_buy_price - self.avg_sell_price) / (self.avg_sell_price - self.stoploss), 4)

    @property
    def risk(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return round((self.avg_buy_price - self.stoploss) * self.quantity, 4)
        return round((self.stoploss - self.avg_sell_price) * self.quantity, 4)

    @property
    def charges(self):
        return round(self.pnl / 10, 4)

    @property
    def gross_pnl(self):
        return self.pnl - self.charges

    @property
    def cost(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return self.avg_buy_price * self.quantity
        return self.avg_sell_price * self.quantity

    @property
    def profit_distance(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return (self.target - self.avg_buy_price) / self.avg_buy_price
        return (self.avg_sell_price - self.target) / self.avg_sell_price

    @property
    def stop_distance(self):
        if self.trade_type == TRADE_TYPE.BUY:
            return round((self.avg_buy_price - self.stoploss) / self.avg_buy_price, 4)
        return round((self.stoploss - self.avg_sell_price) / self.avg_sell_price, 4)

    @property
    def acc_balance(self):
        return self.gross_pnl

    def __str__(self):
        return f"{self.symbol} {self.trade_type} {self.quantity} @ {self.breakeven_point}"
