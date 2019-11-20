from django_pandas.io import read_frame
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django_filters import rest_framework as filters

from .models import Sale
from .filters import SaleFilter
from .forms import SaleForm, SearchForm

import csv
import io
from django.views import generic
from django.http import HttpResponse
from .forms import CSVUploadForm
from datetime import datetime, date, timedelta
from dateutil import relativedelta
from django.shortcuts import redirect
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import calendar
import pandas as pd
import numpy as np


class SaleFilterView(LoginRequiredMixin, FilterView):
    model = Sale
    filterset_class = SaleFilter
    # デフォルトの並び順を新しい順とする
    queryset = Sale.objects.all().order_by('-created_at')

    # クエリ未指定の時に全件検索を行うために以下のオプションを指定（django-filter2.0以降）
    strict = False

    # 1ページあたりの表示件数
    paginate_by = 10

    # 検索条件をセッションに保存する or 呼び出す
    def get(self, request, **kwargs):
        if request.GET:
            request.session['query'] = request.GET
        else:
            request.GET = request.GET.copy()
            if 'query' in request.session.keys():
                for key in request.session['query'].keys():
                    request.GET[key] = request.session['query'][key]

        return super().get(request, **kwargs)


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    success_url = reverse_lazy('index')

# 登録画面


class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    success_url = reverse_lazy('index')


# 更新画面


class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    success_url = reverse_lazy('index')


# 削除画面
class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    success_url = reverse_lazy('index')

# インポート処理


class SaleImport(generic.FormView):
    template_name = 'app/sale_import.html'
    success_url = reverse_lazy('index')
    form_class = CSVUploadForm

    def form_valid(self, form):
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csvfile = io.TextIOWrapper(form.cleaned_data['file'], encoding='utf-8')
        reader = csv.reader(csvfile)
        dt_time = datetime.now()
        # 1行ずつ取り出し、作成していく
        for row in reader:
            sale, created = Sale.objects.get_or_create(
                store=row[1], sale_date=row[2], defaults=dict(
                    store=1, sale=0, cost=0, created_at=dt_time)
            )
            sale.store = row[1]
            sale.sale_date = row[2]
            sale.sale = row[3]
            sale.cost = row[4]
            sale.created_at = dt_time
            sale.save()
        return super().form_valid(form)


def sale_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sale.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せます。
    writer = csv.writer(response)
    for sale in Sale.objects.all():
        writer.writerow(
            [sale.id, sale.store, sale.sale_date, sale.sale, sale.cost])
    return response
# 月集計


@login_required(login_url='/admin/login/')
def SaleMonthView(request):
    header = []
    record = []
    if 'Calc_Month_year' in request.POST:
        # 日付の受け取り
        start_year = int(request.POST["Calc_Month_year"])
        start_month = int(request.POST["Calc_Month_month"])
        start_date = date(start_year, start_month, 1)
        final_Date = date(start_year, start_month+1, 1) - timedelta(days=1)
        start_date_pre = start_date - relativedelta.relativedelta(years=1)
        final_Date_pre = final_Date - relativedelta.relativedelta(years=1)
        sale_data = Sale.objects.all()
        df = read_frame(sale_data, fieldnames=[
                        'id', 'sale_date', 'sale', 'cost', 'created_at', 'store'])
        # 粗利に変換
        df['cost'] = df['sale'] - df['cost']
        # 日付でインデックス
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df.set_index('sale_date', inplace=True)
        # 要らないもの削除
        df.drop(['created_at'], axis=1, inplace=True)
        df.drop(['id'], axis=1, inplace=True)
        # 店舗条件
        if 'store_id' in request.POST:
            store_id = int(request.POST["store_id"])
            if store_id > 0:
                df = df[df['store'] == store_id]
        # 日付でグループ化
        df = df.groupby(['sale_date']).sum()
        # ひと月のDF作成
        month_di = pd.date_range(start=start_date, end=final_Date, freq='D')
        pre_month_di = pd.date_range(
            start=start_date_pre, end=final_Date_pre, freq='D')
        month_df = pd.DataFrame(month_di, index=month_di, columns={'sale_day'})
        pre_month_df = pd.DataFrame(
            pre_month_di, index=pre_month_di, columns={'sale_day'})
        now_df = pd.concat([month_df, df], axis=1, join_axes=[month_df.index])
        pre_df = pd.concat([pre_month_df, df], axis=1,
                           join_axes=[pre_month_df.index])
        now_df['sale_day'] = now_df['sale_day'].dt.day
        pre_df['sale_day'] = pre_df['sale_day'].dt.day
        # 前年と結合
        now_df.set_index('sale_day', inplace=True)
        pre_df.set_index('sale_day', inplace=True)
        df = pd.concat([now_df, pre_df], axis=1)
        df.columns = ['売上', '粗利', '前年売上', '前年粗利']
        # 欠損を0に
        df.fillna(0, inplace=True)
        # 累積計追加
        df = pd.concat([df, df['売上'].cumsum()], axis=1)
        df = pd.concat([df, df['粗利'].cumsum()], axis=1)
        df = pd.concat([df, df['前年売上'].cumsum()], axis=1)
        df = pd.concat([df, df['前年粗利'].cumsum()], axis=1)
        df.columns = ['売上', '粗利', '前年売上', '前年粗利',
                      '売上累計', '粗利累計', '前年売上累計', '前年粗利累計']
        df = df.astype(np.int64)
        df = pd.concat([df, df['売上累計'] / df['前年売上累計']], axis=1)
        df = pd.concat([df, df['粗利累計'] / df['前年粗利累計']], axis=1)

        df.columns = ['売上', '粗利', '前年売上', '前年粗利', '売上累計',
                      '粗利累計', '前年売上累計', '前年粗利累計', '売上比', '粗利比']
        df['売上比'] = (df['売上比'].replace([np.inf, -np.inf], np.nan))
        df['粗利比'] = (df['粗利比'].replace([np.inf, -np.inf], np.nan))
        df.fillna(0, inplace=True)

        df['売上比'] = df['売上比'].apply('{:.0%}'.format)
        df['粗利比'] = df['粗利比'].apply('{:.0%}'.format)
        df = df.round({'売上比': 1, '粗利比': 1})

        header = df.columns
        record = df.reset_index().values.tolist()
    param = {
        'login_user': request.user,
        'search_form': SearchForm(),
        'header': header,
        'record': record
    }
    return render(request, 'app/sale_month.html', param)
    # 入力がなければテンプレートを表示
