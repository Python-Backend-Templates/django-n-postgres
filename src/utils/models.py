from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата и время создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Дата и время последнего обновления")
    )

    class Meta:
        abstract = True
