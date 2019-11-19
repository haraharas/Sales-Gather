from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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
        default=1,
        null=False
    )
