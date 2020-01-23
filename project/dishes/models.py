import datetime

from django.db import models
from django.utils.text import slugify


class Market(models.Model):
    name = models.CharField(max_length=20)
    # orders_count = models.IntegerField(default=0)
    # orders_total_by_price_1 = models.IntegerField(default=0)
    # orders_total_by_price_2 = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, null=True)
    dishes_quantity = models.IntegerField(default=0)
    total_dishes_quantity = models.IntegerField(default=0)
    total_by_price_1 = models.IntegerField(default=0)
    total_by_price_2 = models.IntegerField(default=0)
    date = models.DateField()

    slug = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        slug_name = str(self.market) + '-' + str(self.date) + \
            '-' + str(datetime.datetime.now().microsecond)
        self.slug = slugify('market ' + slug_name)  # allow_unicode=True
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return self.market.name


class Dish(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    number = models.IntegerField()
    code = models.IntegerField()
    bar_code = models.BigIntegerField()
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=25)
    rest = models.IntegerField()
    quantity = models.IntegerField(default=0)
    return_by_defect = models.IntegerField()
    exchange_by_defect = models.IntegerField()
    price_1 = models.IntegerField(default=0)
    price_2 = models.IntegerField(default=0)

    approve = models.BooleanField(default=False)
    cancel = models.BooleanField(default=False)


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['number']


class UniqueDish(models.Model):
    number = models.IntegerField()
    code = models.IntegerField()
    bar_code = models.BigIntegerField()
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=25)
    rest = models.IntegerField()
    quantity = models.IntegerField(default=0)
    return_by_defect = models.IntegerField()
    exchange_by_defect = models.IntegerField()
    price_1 = models.IntegerField(default=0)
    price_2 = models.IntegerField(default=0)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name
