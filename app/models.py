from django.db import models
from django.core import validators
from django.utils import timezone
# Create your models here.


class Sale(models.Model):

    STORE_CHOICES = (
        (1, '卸部門'),
        (2, '加工部門'),
        (3, '配送部'),
        (4, '観光通り店'),
        (5, 'カロム店'),
        (6, '思案橋店'),
        (7, 'ブライダル'),
    )

    store = models.IntegerField(
        verbose_name='店舗',
        choices=STORE_CHOICES,
    )

    sale_date = models.DateField(
        verbose_name='売上日',
    )

    sale = models.IntegerField(
        verbose_name='売上額',
        blank=False,
        null=False,
    )

    cost = models.IntegerField(
        verbose_name='仕入額',
        blank=False,
        null=False,
    )
    memo = models.CharField(
        verbose_name='備考',
        max_length=255,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        verbose_name='更新日',
        auto_now_add=True
    )

    csv_import = models.BooleanField(
        null=True,
    )

    def __str__(self):
        return self.memo

    class Meta:
        verbose_name = '売上'
        verbose_name_plural = '売上'
