from django_filters import filters
from django_filters import FilterSet
from .models import Sale


class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = '%s （降順）'


class SaleFilter(FilterSet):
    class Meta:

        model = Sale
        fields = ('store', 'sale_date', 'sale', 'cost',)


class SaleFilter_Month(FilterSet):
    sale_date_year = filters.NumberFilter(
        label='年', field_name='sale_date', lookup_expr='year')
    sale_date_month = filters.NumberFilter(
        label='月', field_name='sale_date', lookup_expr='month')

    class Meta:

        model = Sale
        fields = ('store', 'sale_date_year', 'sale_date_month')
