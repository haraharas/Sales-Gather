import io
import csv
from django import forms
from .models import Sale
import bootstrap_datepicker_plus as datetimepicker
from datetime import datetime


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

    def clean_file(self):
        file = self.cleaned_data['file']

        # ファイル名が.csvかどうかの確認
        if not file.name.endswith('.csv'):
            raise forms.ValidationError('拡張子がcsvのファイルをアップロードしてください')

        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csv_file = io.TextIOWrapper(file, encoding='utf-8')
        reader = csv.reader(csv_file)
        dt_time = datetime.now()
        # 各行から作った保存前のモデルインスタンスを保管するリスト
        self._instances = []
        try:
            for row in reader:
                sale = Sale(store=row[1],
                            sale_date=row[2], sale=row[3], cost=row[4], created_at=dt_time)
                self._instances.append(sale)
        except UnicodeDecodeError:
            raise forms.ValidationError(
                'ファイルのエンコーディングや、正しいCSVファイルか確認ください。')

        return file

    def save(self):
        for sale in self._instances:
            sale.save()
