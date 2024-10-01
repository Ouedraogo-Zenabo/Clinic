from django.db import models

# Create your models here.

from web.cmodels import (
    ParameterModel,
    CONSTRAINT,
    CommonAbstractModel,
    AutoSlugField,
    StatusModel,
    CommonAbstractModelWithCodeModel,
)
from web.constants import MIN_LENGTH, MEDIUM_LENGTH, BIG_LENGTH


class MailContent(CommonAbstractModel):
    slug = AutoSlugField(
        populate_from="label", always_update=True, max_length=MEDIUM_LENGTH, unique=True
    )
    label = models.CharField("Libellé", max_length=MEDIUM_LENGTH, unique=True)

    class Meta:
        abstract = True


class Clinic(ParameterModel):
    address = models.CharField("Adresse", max_length=MIN_LENGTH)

    class Meta:
        ordering = ["label"]
        verbose_name = "clinique"
        verbose_name_plural = "cliniques"
        permissions = [
            ("list_clinic", "Can list clinic"),
            ("export_clinic", "Can export clinic"),
            ("import_clinic", "Can import clinic"),
            ("print_clinic", "Can print clinic"),
        ]



class Pharmacie(ParameterModel):
    address = models.CharField("Adresse", max_length=MIN_LENGTH)

    class Meta:
        ordering = ["label"]
        verbose_name = "pharmacie"
        verbose_name_plural = "pharmacies"
        permissions = [
            ("list_pharmacie", "Can list pharmacie"),
            ("export_pharmacie", "Can export pharmacie"),
            ("import_pharmacie", "Can import pharmacie"),
            ("print_pharmacie", "Can print pharmacie"),
        ]
