import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, FormView, ListView, DetailView

from .models import Order, Dish, UniqueDish
from .forms import UploadFileForm
from .filters import MarketFilterSet, MarketDetailFilterSet, StatisticsFilterSet


class FilteredHomeListView(ListView):
    template_name = 'home.html'
    form_class = UploadFileForm
    model = Order

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        files = request.FILES.getlist('file_field')

        for file in files:
            # Find 'market' and 'date'
            self.process_rows_of_file_to_find_market_and_date(file.get_array())

            # Create order from found 'market' and 'date'
            self.kwargs['order'] = self.create_order()

            # Find and create 'dishes'
            self.process_rows_of_file_to_find_dishes(file.get_array())

        # return HttpResponse('Uploaded!')

        return redirect('/')

    def process_rows_of_file_to_find_market_and_date(self, rows):
        for row in rows:
            self.process_items_of_row_to_find_market_and_date(row)

    def process_items_of_row_to_find_market_and_date(self, row):
        for row_item in row:
            if self.row_item_valid(row_item):
                self.extract_market(row_item)
                self.extract_date(row_item)

    def extract_market(self, row_item):
        if 'Гипермаркет' in row_item:
            start_index = row_item.find('Гипермаркет')
            market = row_item[slice(start_index, len(row_item))]
            self.kwargs['market'] = market

    def extract_date(self, row_item):
        if 'Заказ поставщику' in row_item:
            date_string = row_item[slice(-9, len(row_item))]
            date_object = datetime.datetime.strptime(date_string, "%d.%m.%Y").date()
            self.kwargs['date'] = date_object

    def create_order(self):
        if 'date' in self.kwargs and 'market' in self.kwargs:
            return Order.objects.create(date=self.kwargs['date'],
                                        buyer=self.kwargs['market'])

    def process_rows_of_file_to_find_dishes(self, rows):
        for row_index, row in enumerate(rows):
            self.process_items_of_row_to_find_dishes(row_index, row, rows)

    def process_items_of_row_to_find_dishes(self, row_index, row, rows):
        for row_item in row:
            # Determining that from this row begins dishes
            if row_item == '№':
                self.create_dishes(row_index, rows)

    def create_dishes(self, row_index, rows):
        for dish_index in range(row_index + 1, len(rows)):
            dishes_start_row = rows[dish_index]
            dish = self.validate_dish_values(dishes_start_row)

            try:
                unique_dish = UniqueDish.objects.get(code=dish[1])
                unique_dish.quantity += dish[6]
                unique_dish.return_by_defect += dish[7]
                unique_dish.exchange_by_defect += dish[8]
                unique_dish.save()
            except UniqueDish.DoesNotExist:
                UniqueDish.objects.get_or_create(number=dish[0],
                                                 code=dish[1],
                                                 bar_code=dish[2],
                                                 name=dish[3],
                                                 unit=dish[4],
                                                 rest=dish[5],
                                                 quantity=dish[6],
                                                 return_by_defect=dish[7],
                                                 exchange_by_defect=dish[8])

            Dish.objects.create(order=self.kwargs['order'],
                                number=dish[0],
                                code=dish[1],
                                bar_code=dish[2],
                                name=dish[3],
                                unit=dish[4],
                                rest=dish[5],
                                quantity=dish[6],
                                return_by_defect=dish[7],
                                exchange_by_defect=dish[8])

    @staticmethod
    def row_item_valid(row_item):
        return row_item and type(row_item) == str

    @staticmethod
    def validate_dish_values(dish):
        for i in range(0, len(dish)):
            if i != 3 and i != 4:
                dish[i] = int(dish[i]) if dish[i] else 0
        return dish


class HomeListView(FilteredHomeListView):
    filterset_class = MarketFilterSet
    paginate_by = 20


class FilteredOrderDetailView(FilteredHomeListView):
    model = Dish
    template_name = 'order_detail.html'

    def get_queryset(self):
        queryset = super().get_queryset().filter(order__slug=self.kwargs['slug'])
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['object'] = Order.objects.get(slug=self.kwargs['slug'])
        return context


class OrderDetailView(FilteredOrderDetailView):
    filterset_class = MarketDetailFilterSet


# class OrderDetailView(DetailView):
#     model = Order
#     template_name = 'order_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         context['order_dishes'] = self.object.dish_set.all()
#         return context


class DishDetailView(DetailView):
    model = Dish
    template_name = 'dish_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dishes'] = Dish.objects.filter(code=self.object.code)
        return context


# class StatisticsListView(ListView):
#     model = UniqueDish
#     template_name = 'statistics.html'
#
#     def get_queryset(self):
#         self.queryset = UniqueDish.objects.all()
#
#         for dish in self.queryset:
#             dish_pk_in_list = Dish.objects.filter(code=dish.code)[0]
#             dish.pk_in_dish_list = dish_pk_in_list.pk
#
#         return self.queryset


class FilteredStatisticsListView(FilteredHomeListView):
    model = UniqueDish
    template_name = 'statistics.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for dish in self.filterset.qs:
            dish_pk_in_list = Dish.objects.filter(code=dish.code)[0]
            dish.pk_in_dish_list = dish_pk_in_list.pk

        context['filterset'] = self.filterset

        return context


class StatisticsListView(FilteredStatisticsListView):
    filterset_class = StatisticsFilterSet