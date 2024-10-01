from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.choices import Choices
from datetime import datetime
from phonenumber_field.modelfields import PhoneNumberField
from web.cmodels import CONSTRAINT, CommonAbstractModel, ParameterModel
from web.cmodels import MEDIUM_LENGTH, MIN_LENGTH


# Create your models here.


class User(AbstractUser, CommonAbstractModel):
    USERNAME_FIELD = "matricule"

    first_name = models.CharField(_("first name"), max_length=MEDIUM_LENGTH)
    last_name = models.CharField(_("last name"), max_length=MEDIUM_LENGTH)
    email = models.EmailField(_("email address"), unique=True)
    birthdate = models.DateField("Date de naissance")
    birthplace = models.CharField("Lieu de naissance", max_length=MIN_LENGTH)
    incorporation_date = models.DateField("Date d'incorporation", null=True, blank=True)
    engagement_date = models.DateField("Date d'engagement", null=True, blank=True)
    promotion_date = models.DateField("Date de promotion", null=True, blank=True)
    matricule = models.CharField(max_length=MIN_LENGTH, unique=True)
    address = models.CharField("Adresse", max_length=MIN_LENGTH, null=True, blank=True)
    photo = models.ImageField(
        "Photo d'identité",
        null=True,
        blank=True,
        help_text="Une image dont la taille n'excède pas 3 Mo",
    )
    folder = models.FileField(
        "Dossier du militaire",
        null=True,
        blank=True,
        help_text="Un fichier numérique contenant l'ensemble éléments du dossier (5 Mo)",
    )
    phone = PhoneNumberField("Numéro de téléphone", unique=True)

    def get_role(self):
        if self.is_staff:
            return "admin"
        elif hasattr(self, "assign"):
            return self.assign.group_assign.name
        else:
            return "-"

    def __str__(self):
        if self.grade:
            return f"{self.grade.label} {self.get_full_name()}  ({self.matricule})"
        return f"{self.get_full_name()}  ({self.matricule})"

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        permissions = [
            ("list_user", "Can list user"),
            ("deactivate_user", "Cant deactivate user"),
            ("change_right_user", "Can change user right"),
            ("access_parameter", "Can access to parameter module"),
            ("access_account", "Can access to account module"),
            ("access_statistics", "Can access to statistics module"),
        ]


class AccountActivationSecret(CommonAbstractModel):
    user = models.OneToOneField(User, on_delete=CONSTRAINT)
    secret = models.CharField(max_length=MIN_LENGTH)


class Assign(CommonAbstractModel):
    assigner = models.ForeignKey(
        User, on_delete=CONSTRAINT, related_name="assigner", null=True, blank=True
    )
    unassigner = models.ForeignKey(
        User, on_delete=CONSTRAINT, related_name="unassigner", null=True, blank=True
    )
    user = models.OneToOneField(
        User, on_delete=CONSTRAINT, related_name="assign", null=True, blank=True
    )

    nomination_date = models.DateField(null=True)
    effective_date = models.DateField(null=True)
    end_date = models.DateField(null=True, blank=True)
    group_assign = models.ForeignKey(
        "auth.Group", on_delete=CONSTRAINT, null=True, blank=True
    )
