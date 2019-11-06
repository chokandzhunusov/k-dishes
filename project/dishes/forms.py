import datetime

from django import forms

from .models import Dish, Order


class UploadFileForm(forms.Form):
    file_field = forms.FileField()
    # file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class DishEditForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['bar_code', 'name', 'quantity', 'price_1', 'price_2']
        labels = {'bar_code': 'Штрих код',
                  'name': 'Наименование',
                  'quantity': 'Кол-во',
                  'price_1': 'Цена (покупочная)',
                  'price_2': 'Цена (продажная)'}


class CommitFileUploadForm(forms.Form):
    buyer = forms.CharField(max_length=255)
