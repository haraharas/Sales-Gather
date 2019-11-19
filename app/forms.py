import io
import csv
from django import forms
from .models import Sale
import bootstrap_datepicker_plus as datetimepicker
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime


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
        self.fields['sale_date'].initial = datetime.now()


class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル', help_text='※拡張子csvのファイルをアップロードしてください。')


# 検索フォーム
STORE_CHOICES = Sale.STORE_CHOICES
YEARS_CHOICES = (
    (2019, '卸部門'),
    (2, '加工部門'),
    (3, '配送部'),
    (4, '観光通り店'),
    (5, 'カロム店'),
    (6, '思案橋店'),
    (7, 'ブライダル'),
)

MONTHS_CHOICES = (
    (11, '卸部門'),
    (2, '加工部門'),
    (3, '配送部'),
    (4, '観光通り店'),
    (5, 'カロム店'),
    (6, '思案橋店'),
    (7, 'ブライダル'),
)


class SearchForm(forms.Form):
    Days = {}
    search = forms.ChoiceField(
        label="店舗",
        widget=forms.Select,
        choices=STORE_CHOICES,
    )
    nen = forms.ChoiceField(
        label="年",
        widget=forms.Select,
        choices=YEARS_CHOICES,
    )
    tsuki = forms.ChoiceField(
        label="月",
        widget=forms.Select,
        choices=MONTHS_CHOICES,
    )

    Start_Date = forms.SelectDateWidget
    Final_Date = forms.SelectDateWidget
