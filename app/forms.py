from django import forms
from .models import Sale
import bootstrap_datepicker_plus as datetimepicker

class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        fields = ('store', 'sale_date', 'sale', 'cost')
        widgets = {
            'store': forms.RadioSelect(),
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


class CreateSaleForm(forms.Form):
    fields = ('store', 'sale_date', 'sale', 'cost')
    store = forms.ChoiceField(
        label='店舗名',
        widget=forms.Select,
        choices=Sale.STORE_CHOICES,
        required=True,
    )
    sale_date = forms.DateField(
        label='売上日',
        required=True,
        widget=datetimepicker.DatePickerInput(
            format='%Y-%m-%d',
            options={
                'locale': 'ja',
                'dayViewHeaderFormat': 'YYYY年 MMMM',
                }
        ),
    )
    sale = forms.IntegerField(
        label='売上高',
        required=True,
    )
    cost = forms.IntegerField(
        label='仕入額',
        required=True,
    )
