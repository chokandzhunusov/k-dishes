from django import forms

from .models import Dish, Order


class UploadFileForm(forms.Form):
    MARKETS = (
        ('', '-------------'),
        ('Гипермаркет 1', 'Гипермаркет 1'),
        ('Гипермаркет 2', 'Гипермаркет 2'),
        ('Гипермаркет 3', 'Гипермаркет 3'),
        ('Гипермаркет 4', 'Гипермаркет 4'),
        ('Гипермаркет 5', 'Гипермаркет 5'),
        ('Гипермаркет 6', 'Гипермаркет 6'),
        ('Гипермаркет 7', 'Гипермаркет 7'),
        ('Гипермаркет 8', 'Гипермаркет 8'),
        ('Гипермаркет 9', 'Гипермаркет 9'),
        ('Гипермаркет 10', 'Гипермаркет 10'),
        ('Гипермаркет 11', 'Гипермаркет 11'),
    )

    market = forms.ChoiceField(choices=MARKETS,
                               required=True,
                               label='Гипермаркет')
    date = forms.DateField(widget=forms.SelectDateWidget(),
                           label='Дата')
    file_field = forms.FileField(label='Файл')


class DishEditForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['bar_code', 'name', 'quantity', 'price_1', 'price_2']
        labels = {'bar_code': 'Штрих код',
                  'name': 'Наименование',
                  'quantity': 'Кол-во',
                  'price_1': 'Цена (покупочная)',
                  'price_2': 'Цена (продажная)'}


class FilterForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['date']

    # DAYS = (
    #     ('', '----------------'),
    #     ('1', 'Январь'),
    #     ('2', 'Февраль'),
    # )
    # days = forms.ChoiceField(choices=DAYS)
