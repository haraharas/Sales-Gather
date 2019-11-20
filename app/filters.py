from django_filters import filters
from django_filters import FilterSet
from .models import Sale


class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = '%s （降順）'


class SaleFilter(FilterSet):
    class Meta:

        model = Sale
        fields = ('store', 'sale_date', 'sale', 'cost',)
