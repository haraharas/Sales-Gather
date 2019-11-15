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


class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル', help_text='※拡張子csvのファイルをアップロードしてください。')
