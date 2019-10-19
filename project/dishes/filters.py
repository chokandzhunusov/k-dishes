import django_filters
from django import forms

from django.contrib.postgres.search import SearchQuery, SearchVector

from .models import *


class MarketFilterSet(django_filters.FilterSet):
    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('format', 'paperback')
        data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    buyer = django_filters.CharFilter(label='Маркет', field_name='buyer', method='filter_buyer')

    day = django_filters.NumberFilter(label='День', field_name='date', method='filter_day')
    month = django_filters.NumberFilter(label='Месяц', field_name='date', method='filter_month')
    year = django_filters.NumberFilter(label='Год', field_name='date', method='filter_year')

    @staticmethod
    def filter_buyer(queryset, name, value):
        result = queryset.filter(buyer__contains=value)

        if not result:
            result = queryset.filter(buyer__contains=value.capitalize())

        return result

    @staticmethod
    def filter_day(queryset, name, value):
        return queryset.filter(date__day=value)

    @staticmethod
    def filter_month(queryset, name, value):
        return queryset.filter(date__month=value)

    @staticmethod
    def filter_year(queryset, name, value):
        return queryset.filter(date__year=value)


class MarketDetailFilterSet(django_filters.FilterSet):
    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('format', 'paperback')
        data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    code = django_filters.NumberFilter(label='Код', field_name='code', method='filter_by_code')
    bar_code = django_filters.NumberFilter(label='Штрихкод', field_name='bar_code', method='filter_by_bar_code')
    quantity = django_filters.NumberFilter(label='Заказ', field_name='quantity', method='filter_by_quantity')

    name = django_filters.CharFilter(label='Продукция', field_name='name', method='filter_by_name')

    @staticmethod
    def filter_by_code(queryset, name, value):
        return queryset.filter(code__icontains=value)

    @staticmethod
    def filter_by_bar_code(queryset, name, value):
        return queryset.filter(bar_code__icontains=value)

    @staticmethod
    def filter_by_quantity(queryset, name, value):
        return queryset.filter(quantity__icontains=value)

    @staticmethod
    def filter_by_name(queryset, name, value):
        result = queryset.filter(name__icontains=value)

        if not result:
            result = queryset.filter(name__icontains=value.capitalize())

        return result


class StatisticsFilterSet(django_filters.FilterSet):
    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('format', 'paperback')
        data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    code = django_filters.NumberFilter(label='Код', field_name='code', method='filter_by_code')
    bar_code = django_filters.NumberFilter(label='Штрихкод', field_name='bar_code', method='filter_by_bar_code')
    quantity = django_filters.NumberFilter(label='Заказ', field_name='quantity', method='filter_by_quantity')

    name = django_filters.CharFilter(label='Продукция', field_name='name', method='filter_by_name')

    @staticmethod
    def filter_by_code(queryset, name, value):
        return queryset.filter(code__icontains=value)

    @staticmethod
    def filter_by_bar_code(queryset, name, value):
        return queryset.filter(bar_code__icontains=value)

    @staticmethod
    def filter_by_quantity(queryset, name, value):
        return queryset.filter(quantity__icontains=value)

    @staticmethod
    def filter_by_name(queryset, name, value):
        result = queryset.filter(name__icontains=value)

        if not result:
            result = queryset.filter(name__icontains=value.capitalize())

        return result
