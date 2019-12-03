from django_filters import filters
from django_filters import FilterSet
from .models import Sale
from datetime import date, timedelta
from django import forms


class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = '%s （降順）'


class SaleFilter(FilterSet):
    sale_date_year = filters.CharFilter(
        field_name="sale_date", lookup_expr='year')
    sale_date_month = filters.CharFilter(
        field_name="sale_date", lookup_expr='month')

    class Meta:
        model = Sale
        fields = ('store', 'sale_date_year', 'sale_date_month',)
