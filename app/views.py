from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django_filters import rest_framework as filters

from .models import Sale
from .filters import SaleFilter, SaleFilter_Month
from .forms import SaleForm, SearchForm

import csv
import io
from django.views import generic
from django.http import HttpResponse
from .forms import CSVUploadForm
from datetime import datetime
from django.shortcuts import redirect
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import calendar


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
    if 'search' in request.POST:
        # requst.POST内にsearchが含まれているかどうか確認
        # フォームの用意
        que_id = int(request.POST["search"])
        nen = int(request.POST["nen"])
        tsuki = int(request.POST["tsuki"])
        hi = calendar.monthrange(nen, tsuki)[1]
        nissuu = []
        for i in range(hi):
            nissuu.append(str(i+1))
        searchform = SearchForm()
        query1 = Sale.objects.filter(store=que_id, sale_date__year=nen, sale_date__month=tsuki).values(
            "sale_date", "store").annotate(Sum('cost'), Sum('sale')).order_by()
        query2 = Sale.objects.filter(store=que_id, sale_date__year=nen-1, sale_date__month=tsuki).values(
            "sale_date", "store").annotate(Sum('cost'), Sum('sale')).order_by()
        store_name = Sale(store=que_id).get_store_display
        gene = []
        sum_col = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for m in nissuu:
            gene_dict = {}
            gene_dict["day"] = int(m)
            for m2 in query1:
                if int(m) == int(m2["sale_date"].day):
                    gene_dict["sale"] = m2["sale__sum"]
                    gene_dict["cost"] = m2["cost__sum"]
            for m2 in query2:
                if int(m) == int(m2["sale_date"].day):
                    gene_dict["sale2"] = m2["sale__sum"]
                    gene_dict["cost2"] = m2["cost__sum"]

            gene_dict["sale"] = gene_dict["sale"] if "sale" in gene_dict else 0
            sum_col[0] = sum_col[0] + gene_dict["sale"]
            gene_dict["sale_sum"] = sum_col[0]

            gene_dict["cost"] = gene_dict["cost"] if "cost" in gene_dict else 0
            sum_col[1] = sum_col[1] + gene_dict["cost"]
            gene_dict["cost_sum"] = sum_col[1]

            gene_dict["arari"] = gene_dict["sale"] - gene_dict["cost"]
            sum_col[2] = sum_col[2] + gene_dict["arari"]
            gene_dict["arari_sum"] = sum_col[2]

            gene_dict["sale2"] = gene_dict["sale2"] if "sale2" in gene_dict else 0
            sum_col[3] = sum_col[3] + gene_dict["sale2"]
            gene_dict["sale_sum2"] = sum_col[3]

            gene_dict["cost2"] = gene_dict["cost2"] if "cost2" in gene_dict else 0
            sum_col[4] = sum_col[4] + gene_dict["cost2"]
            gene_dict["cost_sum2"] = sum_col[4]

            gene_dict["arari2"] = gene_dict["sale2"] - gene_dict["cost2"]
            sum_col[5] = sum_col[5] + gene_dict["arari2"]
            gene_dict["arari_sum2"] = sum_col[5]

            if gene_dict["sale"] == 0:
                gene_dict["sale3"] = 0
            elif gene_dict["sale2"] == 0:
                gene_dict["sale3"] = 1
            else:
                gene_dict["sale3"] = gene_dict["sale"] / gene_dict["sale2"]
            gene_dict["sale3"] = int(gene_dict["sale3"] * 100)

            if gene_dict["sale_sum"] == 0:
                gene_dict["sale_sum3"] = 0
            elif gene_dict["sale_sum2"] == 0:
                gene_dict["sale_sum3"] = 1
            else:
                gene_dict["sale_sum3"] = gene_dict["sale_sum"] / \
                    gene_dict["sale_sum2"]
            gene_dict["sale_sum3"] = int(gene_dict["sale_sum3"] * 100)

            if gene_dict["cost"] == 0:
                gene_dict["cost3"] = 0
            elif gene_dict["cost2"] == 0:
                gene_dict["cost3"] = 1
            else:
                gene_dict["cost3"] = gene_dict["cost"] / gene_dict["cost2"]
            gene_dict["cost3"] = int(gene_dict["cost3"] * 100)

            if gene_dict["cost_sum"] == 0:
                gene_dict["cost_sum3"] = 0
            elif gene_dict["cost_sum2"] == 0:
                gene_dict["cost_sum3"] = 1
            else:
                gene_dict["cost_sum3"] = gene_dict["cost_sum"] / \
                    gene_dict["cost_sum2"]
            gene_dict["cost_sum3"] = int(gene_dict["cost_sum3"] * 100)

            if gene_dict["arari"] == 0:
                gene_dict["arari3"] = 0
            elif gene_dict["arari2"] == 0:
                gene_dict["arari3"] = 1
            else:
                gene_dict["arari3"] = gene_dict["arari"] / gene_dict["arari2"]
            gene_dict["arari3"] = int(gene_dict["arari3"] * 100)

            if gene_dict["arari_sum"] == 0:
                gene_dict["arari_sum3"] = 0
            elif gene_dict["arari_sum2"] == 0:
                gene_dict["arari_sum3"] = 1
            else:
                gene_dict["arari_sum3"] = gene_dict["arari_sum"] / \
                    gene_dict["arari_sum2"]
            gene_dict["arari_sum3"] = int(gene_dict["arari_sum3"] * 100)

            gene.append(gene_dict)
    else:
        query1 = Sale.objects.filter().values("sale_date", "store").annotate(
            Sum('cost'), Sum('sale')).order_by()
        query2 = Sale.objects.filter().values("sale_date", "store").annotate(
            Sum('cost'), Sum('sale')).order_by()
        store_name = "条件を入力してください"
        searchform = SearchForm()
        gene = []
    #　共通処理
    param1 = {
        'login_user': request.user,
        'search_form': searchform,
        "q": gene,
        "store_name": store_name,
    }
    return render(request, 'app/sale_month.html', param1)
