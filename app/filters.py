from django_filters import filters
from django_filters import FilterSet
from .models import Sale
from datetime import date, timedelta
from django import forms


class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = '%s （降順）'


YEAR_CHOICES = (
    [(int(i), str(i) + '年') for i in range(2018, 2040)]
)
MONTH_CHOICES = (
    [(int(i), str(i) + '月') for i in range(1, 13)]
)


class SaleFilter(FilterSet):
    sale_date_year = filters.ChoiceFilter(
        field_name="sale_date", lookup_expr='year', label='年検索', choices=YEAR_CHOICES)
    sale_date_month = filters.ChoiceFilter(
        field_name="sale_date", lookup_expr='month', label='月検索', choices=MONTH_CHOICES)

    class Meta:
        model = Sale
        fields = ('store', 'sale_date_year', 'sale_date_month',)
