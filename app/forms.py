import io
import csv
from django import forms
from .models import Sale
import bootstrap_datepicker_plus as datetimepicker
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta


class SaleForm(LoginRequiredMixin, forms.ModelForm):

    class Meta:
        model = Sale
        fields = ('store', 'sale_date', 'sale', 'cost')
        widgets = {
            'store': forms.Select,
            'sale_date': datetimepicker.DatePickerInput(
                format='%Y-%m-%d',
                options={
                    'locale': 'ja',
                    'dayViewHeaderFormat': 'YYYY年 MMMM',
                }
            ),
            'sale': forms.NumberInput(attrs={'min': 1}),
            'cost': forms.NumberInput(attrs={'min': 1}),
        }
    # __init__上でフィールドを初期化します

    def __init__(self, * args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['sale'].initial = 2
        self.fields['sale_date'].initial = date.today()


class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル', help_text='※拡張子csvのファイルをアップロードしてください。')


# 検索フォーム
STORE_CHOICES = Sale.STORE_CHOICES


class SearchForm(forms.Form):
    store_id = forms.ChoiceField(
        label="　店舗　",
        widget=forms.Select,
        choices=STORE_CHOICES,
        required=False,
    )

    Calc_Month = forms.DateField(
        label="　計算月　",
        widget=forms.SelectDateWidget,
    )

    def __init__(self, * args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        this_day = date.today()
        self.fields['Calc_Month'].initial = date(
            this_day.year, this_day.month, 1)
