from django.http import HttpResponse
from django.core.mail import BadHeaderError, send_mail
from django.conf import settings
import io
import csv
from django import forms
from .models import Sale
import bootstrap_datepicker_plus as datetimepicker
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta


@login_required
def user_store(requset):
    user_store = requset.user
    return user_store.id


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
        self.fields['sale_date'].initial = date.today()


class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='', help_text='※拡張子csvのファイルをアップロードしてください。')


def id_to_store(store_id):
    if store_id == 1:
        return '卸部門'
    elif store_id == 2:
        return '加工部門'
    elif store_id == 3:
        return '配送部'
    elif store_id == 4:
        return '観光通り店'
    elif store_id == 5:
        return 'カロム店'
    elif store_id == 6:
        return '思案橋店'
    elif store_id == 7:
        return 'ブライダル'


STORE_CHOICES = (
    (0, '全部門'),
    (1, '卸部門'),
    (2, '加工部門'),
    (3, '配送部'),
    (4, '観光通り店'),
    (5, 'カロム店'),
    (6, '思案橋店'),
    (7, 'ブライダル'),
)


class MonthForm(forms.Form):
    store_id = forms.ChoiceField(
        label="　店舗　",
        widget=forms.Select,
        choices=STORE_CHOICES,
        required=False,
    )

    Calc_Month = forms.DateField(
        label="　計算月　",
        widget=forms.SelectDateWidget(
            years=[x for x in range(2018, date.today().year+2)]),
        required=False,
    )

    def __init__(self, * args, **kwargs):
        super(MonthForm, self).__init__(*args, **kwargs)
        this_day = date.today()
        self.fields['Calc_Month'].initial = date(
            this_day.year, this_day.month, 1)


class YearForm(forms.Form):
    store_id = forms.ChoiceField(
        label="　店舗　",
        widget=forms.Select,
        choices=STORE_CHOICES,
        required=True,
    )

    Calc_Month = forms.DateField(
        label="　計算月　",
        widget=forms.SelectDateWidget(
            years=[x for x in range(2018, date.today().year+2)]),
        required=True,
    )

    def __init__(self, * args, **kwargs):
        super(YearForm, self).__init__(*args, **kwargs)
        this_day = date.today()
        self.fields['Calc_Month'].initial = date(
            this_day.year, this_day.month, 1)


class ContactForm(forms.Form):
    name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "お名前",
        }),
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': "メールアドレス",
        }),
    )
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': "お問い合わせ内容",
        }),
    )

    def send_email(self):
        subject = "お問い合わせ"
        message = self.cleaned_data['message']
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        from_email = '{name} <{email}>'.format(name=name, email=email)
        recipient_list = [settings.EMAIL_HOST_USER]  # 受信者リスト
        try:
            send_mail(subject, message, from_email, recipient_list)
        except BadHeaderError:
            return HttpResponse("無効なヘッダが検出されました。")
