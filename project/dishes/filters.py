import django_filters
from django import forms

from .models import Order, Dish, UniqueDish


class MarketFilterSet(django_filters.FilterSet):
    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('format', 'paperback')
        data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    buyer = django_filters.CharFilter(label='Маркет',
                                      field_name='buyer',
                                      method='filter_buyer')

    day = django_filters.NumberFilter(label='День',
                                      field_name='date',
                                      method='filter_day')

    month = django_filters.NumberFilter(label='Месяц',
                                        field_name='date',
                                        method='filter_month')

    year = django_filters.NumberFilter(label='Год',
                                       field_name='date',
                                       method='filter_year')

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

    code = django_filters.NumberFilter(label='Код',
                                       field_name='code',
                                       method='filter_by_code')

    bar_code = django_filters.NumberFilter(label='Штрихкод',
                                           field_name='bar_code',
                                           method='filter_by_bar_code')

    quantity = django_filters.NumberFilter(label='Заказ',
                                           field_name='quantity',
                                           method='filter_by_quantity')

    name = django_filters.CharFilter(label='Продукция',
                                     field_name='name',
                                     method='filter_by_name')

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
    def __init__(self, request, *args, **kwargs):
        data = request.GET.copy()
        data.setdefault('format', 'paperback')
        data.setdefault('order', '-added')

        self.req_session = request.session

        self.order_ids = []
        self.order_by_years = Order.objects.none()
        self.order_by_months = Order.objects.none()
        self.empty_year = False
        super().__init__(data, *args, **kwargs)

    YEARS = (
        (2019, ("2019")),
        (2020, ("2020")),
        (2021, ("2021")),
        (2022, ("2022")),
        (2023, ("2023")),
    )

    MONTHS = (
        (1, 'Январь'),
        (2, 'Февраль'),
        (3, 'Март'),
        (4, 'Апрель'),
        (5, 'Май'),
        (6, 'Июнь'),
        (7, 'Июль'),
        (8, 'Август'),
        (9, 'Сентябрь'),
        (10, 'Октябрь'),
        (11, 'Ноябрь'),
        (12, 'Декабрь'),
    )

    DAYS = (
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'),
        (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12'), (13, '13'),
        (14, '14'), (15, '15'), (16, '16'), (17, '17'), (18, '18'), (19, '19'),
        (20, '20'), (21, '21'), (22, '22'), (23, '23'), (24, '24'), (25, '25'),
        (26, '26'), (27, '27'), (28, '28'), (29, '29'), (30, '30'), (31, '31'),
    )

    year = django_filters.MultipleChoiceFilter(
        label='Год', field_name='year',
        choices=YEARS,
        method='filter_by_year',
        widget=forms.CheckboxSelectMultiple)

    month = django_filters.MultipleChoiceFilter(
        label='Месяц', field_name='month',
        choices=MONTHS,
        method='filter_by_month',
        widget=forms.CheckboxSelectMultiple)

    day = django_filters.MultipleChoiceFilter(
        label='День', field_name='day',
        choices=DAYS,
        method='filter_by_day',
        widget=forms.CheckboxSelectMultiple)

    def filter_by_year(self, queryset, name, value):
        for u_dish in queryset:
            u_dish.quantity = 0
            u_dish.price_1_total = 0
            u_dish.price_2_total = 0
        for year in value:
            for order in Order.objects.filter(date__year=year):
                self.order_by_years |= Order.objects.filter(pk=order.pk)
                self.order_ids.append(order.pk)
                order_dishes = order.dish_set.all()
                for u_dish in queryset:
                    try:
                        dish = order_dishes.get(code=u_dish.code)
                        u_dish.quantity += dish.quantity
                        u_dish.price_1_total += dish.price_1 * dish.quantity
                        u_dish.price_2_total += dish.price_2 * dish.quantity
                    except Dish.DoesNotExist:
                        pass

        self.req_session['order_ids'] = self.order_ids

        if not self.order_by_years:
            self.empty_year = True

        return queryset

    def filter_by_month(self, queryset, name, value):
        self.order_ids = []
        if self.order_by_years:
            for u_dish in queryset:
                u_dish.quantity = 0
                u_dish.price_1_total = 0
                u_dish.price_2_total = 0
            for month in value:
                for order in self.order_by_years.filter(date__month=month):
                    self.order_by_months |= Order.objects.filter(pk=order.pk)
                    self.order_ids.append(order.pk)
                    order_dishes = order.dish_set.all()
                    for u_dish in queryset:
                        try:
                            dish = order_dishes.get(code=u_dish.code)
                            u_dish.quantity += dish.quantity
                            u_dish.price_1_total += dish.price_1 * dish.quantity
                            u_dish.price_2_total += dish.price_2 * dish.quantity
                        except Dish.DoesNotExist:
                            pass
        else:
            if not self.empty_year:
                for month in value:
                    for order in Order.objects.filter(date__month=month):
                        self.order_by_months |= Order.objects.filter(pk=order.pk)
                        self.order_ids.append(order.pk)
                        order_dishes = order.dish_set.all()
                        for u_dish in queryset:
                            try:
                                dish = order_dishes.get(code=u_dish.code)
                                u_dish.quantity += dish.quantity
                                u_dish.price_1_total += dish.price_1 * dish.quantity
                                u_dish.price_2_total += dish.price_2 * dish.quantity
                            except Dish.DoesNotExist:
                                pass
        self.req_session['order_ids'] = self.order_ids
        return queryset

    def filter_by_day(self, queryset, name, value):
        self.order_ids = []
        if self.order_by_months:
            for u_dish in queryset:
                u_dish.quantity = 0
                u_dish.price_1_total = 0
                u_dish.price_2_total = 0
            for day in value:
                for order in self.order_by_months.filter(date__day=day):
                    self.order_ids.append(order.pk)
                    order_dishes = order.dish_set.all()
                    for u_dish in queryset:
                        try:
                            dish = order_dishes.get(code=u_dish.code)
                            u_dish.quantity += dish.quantity
                            u_dish.price_1_total += dish.price_1 * dish.quantity
                            u_dish.price_2_total += dish.price_2 * dish.quantity
                        except Dish.DoesNotExist:
                            pass

        elif self.order_by_years:
            for u_dish in queryset:
                u_dish.quantity = 0
                u_dish.price_1_total = 0
                u_dish.price_2_total = 0
            for day in value:
                for order in self.order_by_years.filter(date__day=day):
                    self.order_ids.append(order.pk)
                    order_dishes = order.dish_set.all()
                    for u_dish in queryset:
                        try:
                            dish = order_dishes.get(code=u_dish.code)
                            u_dish.quantity += dish.quantity
                            u_dish.price_1_total += dish.price_1 * dish.quantity
                            u_dish.price_2_total += dish.price_2 * dish.quantity
                        except Dish.DoesNotExist:
                            pass
        else:
            if not self.empty_year:
                for day in value:
                    for order in Order.objects.filter(date__day=day):
                        self.order_ids.append(order.pk)
                        order_dishes = order.dish_set.all()
                        for u_dish in queryset:
                            try:
                                dish = order_dishes.get(code=u_dish.code)
                                u_dish.quantity += dish.quantity
                                u_dish.price_1_total += dish.price_1 * dish.quantity
                                u_dish.price_2_total += dish.price_2 * dish.quantity
                            except Dish.DoesNotExist:
                                pass
        self.req_session['order_ids'] = self.order_ids
        return queryset
