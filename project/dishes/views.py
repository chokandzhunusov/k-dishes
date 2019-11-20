from datetime import datetime
import datefinder
from django.urls import reverse
from django.shortcuts import redirect, render

import django.views.generic as views
from django.http import QueryDict, HttpResponse

from .models import Market, Order, Dish, UniqueDish
from .forms import UploadFileForm, DishEditForm, UploadDishPriceForm
from .filters import MarketFilterSet, MarketDetailFilterSet, StatisticsFilterSet


class CreateMarketsView(views.View):
    def get(self, request, *args, **kwargs):
        for i in range(1, 41):
            Market.objects.get_or_create(name=f'Гипермаркет {i}')
        return HttpResponse('Done')


class UploadDishPriceView(views.FormView):
    form_class = UploadDishPriceForm
    template_name = 'upload_dish_price.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('file_field')
        for file in files:
            self.data = file.get_array()

            self.numbers = []
            self.names = []
            self.price_1 = []
            self.price_2 = []

            self.column_number_index = int()
            self.column_name_index = int()
            self.column_price_1_index = int()
            self.column_price_2_index = int()

            for row_index, row in enumerate(self.data):
                for row_item in row:
                    if row_item == '№':
                        self.dishes_header_row_index = row_index

            for row_item_index, row_item in enumerate(
                    self.data[self.dishes_header_row_index]):

                if row_item == '№':
                    self.column_number_index = row_item_index
                elif row_item == 'наименование':
                    self.column_name_index = row_item_index
                elif row_item == 'Своя цена':
                    self.column_price_1_index = row_item_index
                elif row_item == 'Продажная цена':
                    self.column_price_2_index = row_item_index

            for i in range(self.dishes_header_row_index + 1, len(self.data)):
                if isinstance(self.data[i][self.column_number_index], int):
                    self.numbers.append(self.data[i][self.column_number_index])
                    self.names.append(self.data[i][self.column_name_index])
                    self.price_1.append(self.data[i][self.column_price_1_index])
                    self.price_2.append(self.data[i][self.column_price_2_index])

            for i in range(len(self.numbers)):
                try:
                    u_dish = UniqueDish.objects.get(name=self.names[i])
                    u_dish.price_1 = self.price_1[i]
                    u_dish.price_2 = self.price_2[i]
                    u_dish.save()
                except Exception as e:
                    print(e)
            return render(request, 'home.html')


class BaseView(views.View):
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('file_field')
        try:
            for file in files:
                data = file.get_array()
        except:
            request.session['not_exls_file'] = True
            return redirect('home')

        try:
            market, created = Market.objects.get_or_create(name=request.POST['market'])
            day = request.POST['date_day']
            month = request.POST['date_month']
            year = request.POST['date_year']
            date = f'{day}-{month}-{year}'
            date = datetime.strptime(date, "%d-%m-%Y").date()

            self.order = Order.objects.create(
                market=market,
                date=date)
        except:
            try:
                for file in files:
                    data = file.get_array()

                    for row in data:
                        for row_item in row:
                            # Extract market
                            if 'Гипермаркет' in str(row_item):
                                start_index = row_item.find('Гипермаркет')
                                market_name = row_item[slice(start_index, len(row_item))]
                                market_num = [int(s) for s in market_name.split() if s.isdigit()][0]

                                self.market = Market.objects.get(
                                    name__exact=f'Гипермаркет {market_num}')

                            # Extract date
                            if 'Заказ поставщику' in str(row_item):
                                start_index = row_item.find('от')
                                date_name = row_item[slice(start_index, len(row_item))]
                                date = list(datefinder.find_dates(date_name))
                                self.date = date[0].date()

                    # Check if there is market name in file
                    self.order = Order.objects.create(
                        market=self.market,
                        date=self.date)
            except Exception as e:
                print(e)
                return render(request, 'upload_file.html')

        for file in files:
            self.data = file.get_array()

            self.initialize_columns()
            self.initialize_column_indexes()

            self.dishes_header_row_index = int()

            # Find dishes header row and index of that row
            for row_index, row in enumerate(self.data):
                for row_item in row:
                    if row_item == '№':
                        self.dishes_header_row_index = row_index

            self.set_column_indexes()
            self.collect_dishes_by_column()

            for i in range(len(self.numbers)):

                if not self.exchange_by_defects[i]:
                    self.exchange_by_defects[i] = 0

                if not self.return_by_defects[i]:
                    self.return_by_defects[i] = 0

                if not self.rests[i].strip():
                    self.rests[i] = 0

                self.codes[i] = self.codes[i] or 0
                self.bar_codes[i] = self.bar_codes[i] or 0
                self.quantities[i] = self.quantities[i] or 0

                self.update_or_create_unq_dish(i)

                self.unique_dish = UniqueDish.objects.get(code=self.codes[i])

                self.create_dish(i)

        return redirect('/')

    def initialize_columns(self):
        self.numbers = []
        self.codes = []
        self.bar_codes = []
        self.names = []
        self.units = []
        self.rests = []
        self.quantities = []
        self.return_by_defects = []
        self.exchange_by_defects = []

    def initialize_column_indexes(self):
        self.column_number_index = int()
        self.column_name_index = str()
        self.column_code_index = int()
        self.column_bar_code_index = int()
        self.column_quantity_index = int()
        self.column_unit_index = str()
        self.column_rest_index = int()
        self.column_return_by_defect_index = int()
        self.column_exchange_by_defect_index = int()

    def set_column_indexes(self):
        for row_item_index, row_item in enumerate(
                self.data[self.dishes_header_row_index]):

            if row_item == '№':
                self.column_number_index = row_item_index
            elif row_item == 'Товар' or row_item == 'Продукция':
                self.column_name_index = row_item_index
            elif row_item == 'Код':
                self.column_code_index = row_item_index
            elif row_item == 'Штрих-код' or row_item == 'Штрихкод':
                self.column_bar_code_index = row_item_index
            elif row_item.startswith('Остаток'):
                self.column_rest_index = row_item_index
            elif row_item == 'Кол-во' or row_item == 'Заказ':
                self.column_quantity_index = row_item_index
            elif row_item == 'Ед.' or row_item == 'Ед.Изм.':
                self.column_unit_index = row_item_index
            elif row_item.startswith('Обмен'):
                self.column_return_by_defect_index = row_item_index
            elif row_item.startswith('Возврат'):
                self.column_exchange_by_defect_index = row_item_index

    def collect_dishes_by_column(self):
        for i in range(self.dishes_header_row_index + 1, len(self.data)):
            if isinstance(self.data[i][self.column_number_index], int):
                self.numbers.append(self.data[i][self.column_number_index])
                self.codes.append(self.data[i][self.column_code_index])
                self.bar_codes.append(self.data[i][self.column_bar_code_index])
                self.names.append(self.data[i][self.column_name_index])
                self.units.append(self.data[i][self.column_unit_index])
                self.rests.append(self.data[i][self.column_rest_index])
                self.quantities.append(
                    self.data[i][self.column_quantity_index])
                self.return_by_defects.append(
                    self.data[i][self.column_return_by_defect_index])
                self.exchange_by_defects.append(
                    self.data[i][self.column_exchange_by_defect_index])

    def update_or_create_unq_dish(self, i):
        try:
            UniqueDish.objects.get(code=self.codes[i])
        except UniqueDish.DoesNotExist:
            UniqueDish.objects.get_or_create(
                number=self.numbers[i],
                code=self.codes[i],
                bar_code=self.bar_codes[i],
                name=self.names[i],
                unit=self.units[i],
                rest=self.rests[i],
                # quantity=self.quantities[i],
                return_by_defect=self.return_by_defects[i],
                exchange_by_defect=self.exchange_by_defects[i])

    def create_dish(self, i):
        Dish.objects.create(
            order=self.order,
            number=self.numbers[i],
            code=self.codes[i],
            bar_code=self.bar_codes[i],
            name=self.names[i],
            unit=self.units[i],
            rest=self.rests[i],
            quantity=self.quantities[i],
            return_by_defect=self.return_by_defects[i],
            exchange_by_defect=self.exchange_by_defects[i],
            price_1=self.unique_dish.price_1,
            price_2=self.unique_dish.price_2)


class FilteredHomeListView(views.ListView, BaseView):
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
        try:
            if self.request.session['not_exls_file']:
                context['err_msg'] = 'Пожалуйста загрузите файл формата .xls'
                self.request.session['not_exls_file'] = False
        except KeyError:
            pass
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


class FilteredOrderDetailView(views.ListView, BaseView):
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
            context['totall_price_2'] += dish.price_2 * dish.quantity
            context['totall_dishes'] += dish.quantity

        context['object'] = Order.objects.get(slug=self.kwargs['slug'])
        return context


class OrderDetailView(FilteredOrderDetailView):
    filterset_class = MarketDetailFilterSet


class OrderDeleteView(views.DeleteView):
    model = Order
    template_name = 'delete_order.html'
    success_url = '/'


class DishDetailView(views.DetailView, BaseView):
    model = Dish
    template_name = 'dish_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dishes'] = Dish.objects.filter(code=self.object.code)
        context['total_amount_of_dish'] = 0

        for dish in context['dishes']:
            context['total_amount_of_dish'] += dish.quantity
            order = Order.objects.get(pk=dish.order.pk)
            dish_in_order = order.dish_set.all().get(pk=dish.pk)
            total_dish_price_2_in_order = (
                dish_in_order.quantity * dish_in_order.price_2)
            dish.total_dish_price_2_in_order = total_dish_price_2_in_order

        return context


class DishEditView(views.UpdateView):
    model = Dish
    form_class = DishEditForm
    template_name = 'dish_edit.html'

    def get_success_url(self):
        return reverse('dish_detail', args=[self.kwargs['pk']])


class FilteredStatisticsListView(views.ListView):
    model = UniqueDish
    template_name = 'statistics.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        year = datetime.today().year
        month = datetime.today().month
        if not self.request.GET:
            self.request.GET = QueryDict(f'year={year}&month={month}')

        self.filterset = self.filterset_class(self.request,
                                              queryset=queryset)

        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_dish_price_2'] = 0
        context['total_amount_of_dish'] = 0
        for dish in self.filterset.qs:
            try:
                dish_pk_in_list = Dish.objects.filter(code=dish.code)[0]
                dish.pk_in_dish_list = dish_pk_in_list.pk
                context['total_dish_price_2'] += dish.price_2_total
                context['total_amount_of_dish'] += dish.quantity
            except (Dish.DoesNotExist, IndexError) as e:
                pass

        new_qs = []

        for u_dish in self.filterset.qs.order_by('-quantity'):
            if u_dish.quantity > 0:
                new_qs.append(u_dish)

        context['new_qs'] = new_qs
        context['filtered_qs'] = self.filterset.qs
        context['filterset'] = self.filterset
        return context


class StatisticsListView(FilteredStatisticsListView):
    filterset_class = StatisticsFilterSet


class DishStatisticsView(views.DetailView):
    model = UniqueDish
    template_name = 'dish_statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dishes'] = Dish.objects.none()
        context['total_dish_price_2'] = 0

        for order_id in self.request.session['order_ids']:
            order = Order.objects.get(pk=order_id)
            try:
                context['dishes'] |= order.dish_set.all().filter(
                    code=self.object.code).order_by('-quantity')
            except Dish.DoesNotExist:
                pass

        context['total_amount_of_dish'] = 0

        for dish in context['dishes']:
            context['total_amount_of_dish'] += dish.quantity
            order = Order.objects.get(pk=dish.order.pk)
            dish_in_order = order.dish_set.all().get(pk=dish.pk)
            total_dish_price_2_in_order = (
                dish_in_order.quantity * dish_in_order.price_2)
            dish.total_dish_price_2_in_order = total_dish_price_2_in_order
            context['total_dish_price_2'] += total_dish_price_2_in_order

        return context


class UploadFileView(BaseView, views.FormView):
    form_class = UploadFileForm
    template_name = 'upload_file.html'
    success_url = '/'
