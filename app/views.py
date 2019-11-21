from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django_filters import rest_framework as filters
from django.shortcuts import render, redirect

from .models import Sale
from .filters import SaleFilter, SaleFilter_Month
from .forms import SaleForm, CreateSaleForm


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
def SaleCreate(request):
    form = CreateSaleForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data['store'])
        Sale.objects.filter(
            store=form.cleaned_data['store'], sale_date=form.cleaned_data['sale_date']).delete()
        db = Sale()
        db.store = form.cleaned_data['store']
        db.sale_date = form.cleaned_data['sale_date']
        db.sale = form.cleaned_data['sale']
        db.cost = form.cleaned_data['cost']

        Sale.objects.create(
            store=db.store,
            sale_date=db.sale_date,
            sale=db.sale,
            cost=db.cost,
        )
        return redirect('index')
    return render(request, 'app/sale_add.html', {'form': form})

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
