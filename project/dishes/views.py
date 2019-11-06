from datetime import datetime
from dateutil.parser import parse
import datefinder
import json
from django.urls import reverse
from django.shortcuts import redirect, render, HttpResponseRedirect
from django.http import HttpResponse
from django.views.generic import *

from .models import Order, Dish, UniqueDish
from .forms import *
from .filters import MarketFilterSet, MarketDetailFilterSet, StatisticsFilterSet


class BaseView(View):
    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('file_field')
        # request.session['files'] = []

        for file in files:
            data = file.get_array()
            self.commit_order = False

            for row in data:
                for row_item in row:
                    # Extract market
                    if 'Гипермаркет' in str(row_item):
                        self.commit_order = True
                        start_index = row_item.find('Гипермаркет')
                        market = row_item[slice(start_index, len(row_item))]
                        self.kwargs['market'] = market

                    # Extract date
                    if 'Заказ поставщику' in str(row_item):
                        date = list(datefinder.find_dates(row_item))
                        self.kwargs['date'] = date[0].date()

            # Check if there is market name in file
            try:
                self.kwargs['market']
            except KeyError:
                return render(request, 'add_filename.html')

            numbers = []
            codes = []
            bar_codes = []
            names = []
            units = []
            rests = []
            quantities = []
            return_by_defects = []
            exchange_by_defects = []

            dishes_header_row_index = int()

            column_number_index = int()
            column_name_index = str()
            column_code_index = int()
            column_bar_code_index = int()
            column_quantity_index = int()
            column_unit_index = str()
            column_rest_index = int()
            column_return_by_defect_index = int()
            column_exchange_by_defect_index = int()

            # Find dishes header row and index of that row
            for row_index, row in enumerate(data):
                for row_item in row:
                    if row_item == '№':
                        dishes_header_row_index = row_index

            for row_item_index, row_item in enumerate(data[dishes_header_row_index]):
                if row_item == '№':
                    column_number_index = row_item_index
                elif row_item == 'Товар' or row_item == 'Продукция':
                    column_name_index = row_item_index
                elif row_item == 'Код':
                    column_code_index = row_item_index
                elif row_item == 'Штрих-код' or row_item == 'Штрихкод':
                    column_bar_code_index = row_item_index
                elif row_item.startswith('Остаток'):
                    column_rest_index = row_item_index
                elif row_item == 'Кол-во' or row_item == 'Заказ':
                    column_quantity_index = row_item_index
                elif row_item == 'Ед.' or row_item == 'Ед.Изм.':
                    column_unit_index = row_item_index
                elif row_item.startswith('Обмен'):
                    column_return_by_defect_index = row_item_index
                elif row_item.startswith('Возврат'):
                    column_exchange_by_defect_index = row_item_index

            for i in range(dishes_header_row_index + 1, len(data)):
                if isinstance(data[i][column_number_index], int):
                    numbers.append(data[i][column_number_index])
                    codes.append(data[i][column_code_index])
                    bar_codes.append(data[i][column_bar_code_index])
                    names.append(data[i][column_name_index])
                    units.append(data[i][column_unit_index])
                    rests.append(data[i][column_rest_index])
                    quantities.append(data[i][column_quantity_index])
                    return_by_defects.append(data[i][column_return_by_defect_index])
                    exchange_by_defects.append(data[i][column_exchange_by_defect_index])

            if self.commit_order:
                order = Order.objects.create(
                    date=self.kwargs['date'],
                    buyer=self.kwargs['market']
                )
                for i in range(len(numbers)):

                    if not exchange_by_defects[i]:
                        exchange_by_defects[i] = 0

                    if not return_by_defects[i]:
                        return_by_defects[i] = 0

                    if not rests[i].strip():
                        rests[i] = 0

                    codes[i] = codes[i] or 0
                    bar_codes[i] = bar_codes[i] or 0
                    quantities[i] = quantities[i] or 0

                    try:
                        unique_dish = UniqueDish.objects.get(code=codes[i])
                        unique_dish.quantity += int(quantities[i])
                        unique_dish.return_by_defect += int(return_by_defects[i])
                        unique_dish.exchange_by_defect += int(exchange_by_defects[i])
                        unique_dish.save()
                    except UniqueDish.DoesNotExist:
                        UniqueDish.objects.get_or_create(number=numbers[i],
                                                         code=codes[i],
                                                         bar_code=bar_codes[i],
                                                         name=names[i],
                                                         unit=units[i],
                                                         rest=rests[i],
                                                         quantity=quantities[i],
                                                         return_by_defect=return_by_defects[i],
                                                         exchange_by_defect=exchange_by_defects[i])

                    unique_dish = UniqueDish.objects.get(code=codes[i])

                    Dish.objects.create(
                        order=order,
                        number=numbers[i],
                        code=codes[i],
                        bar_code=bar_codes[i],
                        name=names[i],
                        unit=units[i],
                        rest=rests[i],
                        quantity=quantities[i],
                        return_by_defect=return_by_defects[i],
                        exchange_by_defect=exchange_by_defects[i],
                        price_1=unique_dish.price_1,
                        price_2=unique_dish.price_2)
                self.commit_order = False
            else:
                file = {
                    file.name: [
                        {'name': file.name},
                        {'date': str(self.kwargs['date'])},
                        {'data': [numbers, codes, bar_codes, names, units,
                                  rests, quantities, return_by_defects,
                                  exchange_by_defects]}
                    ]
                }
                request.session['files'].append(file)
        if request.session['files']:
            return redirect('commit-file-upload')
        return redirect('/')
        # return HttpResponse('Uploaded!')


class CommitFileUploadView(TemplateView):
    template_name = 'file_commit.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CommitFileUploadView, self).get_context_data(**kwargs)
        context['names'] = []

        for i, file in enumerate(self.request.session['files']):
            file = list(file.values())[0]
            context['names'].append(file[0]['name'])

        return context

    def post(self, request, *args, **kwargs):
        order_names = request.POST.dict()
        del order_names['csrfmiddlewaretoken']

        for i, file in enumerate(self.request.session['files']):
            date = list(file.values())[0][1]['date']
            data = list(file.values())[0][2]['data']
            numbers = data[0]
            codes = data[1]
            bar_codes = data[2]
            names = data[3]
            units = data[4]
            rests = data[5]
            quantities = data[6]
            return_by_defects = data[7]
            exchange_by_defects = data[8]

            order = Order.objects.create(
                date=date,
                buyer=list(order_names.values())[i]
            )
            for i in range(len(numbers)):

                if not exchange_by_defects[i]:
                    exchange_by_defects[i] = 0

                if not return_by_defects[i]:
                    return_by_defects[i] = 0

                if not rests[i].strip():
                    rests[i] = 0

                codes[i] = codes[i] or 0
                bar_codes[i] = bar_codes[i] or 0
                quantities[i] = quantities[i] or 0

                try:
                    unique_dish = UniqueDish.objects.get(code=codes[i])
                    unique_dish.quantity += int(quantities[i])
                    unique_dish.return_by_defect += int(return_by_defects[i])
                    unique_dish.exchange_by_defect += int(exchange_by_defects[i])
                    unique_dish.save()
                except UniqueDish.DoesNotExist:
                    UniqueDish.objects.get_or_create(number=numbers[i],
                                                     code=codes[i],
                                                     bar_code=bar_codes[i],
                                                     name=names[i],
                                                     unit=units[i],
                                                     rest=rests[i],
                                                     quantity=quantities[i],
                                                     return_by_defect=return_by_defects[i],
                                                     exchange_by_defect=exchange_by_defects[i])

                unique_dish = UniqueDish.objects.get(code=codes[i])

                Dish.objects.create(
                    order=order,
                    number=numbers[i],
                    code=codes[i],
                    bar_code=bar_codes[i],
                    name=names[i],
                    unit=units[i],
                    rest=rests[i],
                    quantity=quantities[i],
                    return_by_defect=return_by_defects[i],
                    exchange_by_defect=exchange_by_defects[i],
                    price_1=unique_dish.price_1,
                    price_2=unique_dish.price_2)
        return redirect('/')


class FilteredHomeListView(ListView, BaseView):
    template_name = 'home.html'
    form_class = UploadFileForm
    model = Order

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET,
                                              queryset=queryset)

        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset

        for order in context['filterset'].qs:

            order_total_price_2 = 0

            for dish in order.dish_set.all():
                order_total_price_2 += (dish.price_2 * dish.quantity)

            order.total_price_2 = order_total_price_2
            order.total_dishes = order.dish_set.all().count()

        return context


class HomeListView(FilteredHomeListView):
    filterset_class = MarketFilterSet
    paginate_by = 20


class FilteredOrderDetailView(ListView, BaseView):
    model = Dish
    template_name = 'order_detail.html'

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            order__slug=self.kwargs['slug'])
        self.filterset = self.filterset_class(self.request.GET,
                                              queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['totall_price_2'] = 0
        context['totall_dishes'] = 0

        for dish in context['filterset'].qs:
            # unique_dish = UniqueDish.objects.get(code=dish.code)
            # dish.price_2 = unique_dish.price_2
            context['totall_price_2'] += dish.price_2
            context['totall_dishes'] += dish.quantity

        context['object'] = Order.objects.get(slug=self.kwargs['slug'])
        return context


class OrderDetailView(FilteredOrderDetailView):
    filterset_class = MarketDetailFilterSet


class DishDetailView(DetailView, BaseView):
    model = Dish
    template_name = 'dish_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dishes'] = Dish.objects.filter(code=self.object.code)
        context['total_amount_of_dish'] = 0

        for dish in context['dishes']:
            context['total_amount_of_dish'] += dish.quantity

        return context


class DishEditView(UpdateView):
    model = Dish
    form_class = DishEditForm
    template_name = 'dish_edit.html'

    def get_success_url(self):
        return reverse('dish_detail', args=[self.kwargs['pk']])


class FilteredStatisticsListView(ListView, BaseView):
    model = UniqueDish
    template_name = 'statistics.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        self.filterset = self.filterset_class(self.request.GET,
                                              queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['totall_price_2'] = 0
        context['totall_dishes'] = 0

        for dish in self.filterset.qs:
            try:
                dish_pk_in_list = Dish.objects.filter(code=dish.code)[0]
                dish.pk_in_dish_list = dish_pk_in_list.pk

                context['totall_price_2'] += dish.price_2 * dish.quantity
                context['totall_dishes'] += dish.quantity
            except:
                pass

        context['filterset'] = self.filterset

        return context


class StatisticsListView(FilteredStatisticsListView):
    filterset_class = StatisticsFilterSet


# class CustomFileUpload(FormView, BaseView):
#     form_class = OrderCreateForm
#     template_name = 'custom_file_upload.html'
#
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST, request.FILES)
#
#         files = request.FILES.getlist('file')
#         buyer_object = request.POST.get('buyer')
#         date_string = request.POST.get('date')
#         date_object = datetime.strptime(date_string, "%d.%m.%Y").date()
#
#         self.kwargs['order'] = Order.objects.create(date=date_object,
#                                                     buyer=buyer_object)
#
#         for file in files:
#             print(file)
#             self.process_rows_of_file_to_find_dishes(file.get_array())
#
#         return redirect('/')
