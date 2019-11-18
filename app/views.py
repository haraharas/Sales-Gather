from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django_filters import rest_framework as filters

from .models import Sale
from .filters import SaleFilter, SaleFilter_Month
from .forms import SaleForm

import csv
import io
from django.views import generic
from django.http import HttpResponse
from .forms import CSVUploadForm
from datetime import datetime
from django.shortcuts import redirect


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
    store = 1


# 更新画面
class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    success_url = reverse_lazy('index')


# 削除画面
class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    success_url = reverse_lazy('index')


# 月集計
class SaleMonthView(LoginRequiredMixin, FilterView):
    model = Sale
    template_name = "app/sale_month.html"
    filterset_class = SaleFilter_Month
    queryset = Sale.objects.all().order_by('created_at')
# インポート処理


class SaleImport(generic.FormView):
    template_name = 'app/import.html'
    success_url = reverse_lazy('index')
    form_class = CSVUploadForm

    def form_valid(self, form):
        form.save()
        return redirect('../')


def sale_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sale.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せます。
    writer = csv.writer(response)
    for sale in Sale.objects.all():
        writer.writerow(
            [sale.id, sale.store, sale.sale_date, sale.sale, sale.cost])
    return response
