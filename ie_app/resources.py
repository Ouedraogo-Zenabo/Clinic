from django.contrib.auth import models as auth_models
from django.utils import timezone
from django.contrib import messages
from import_export.widgets import CharWidget

from import_export import fields, resources, widgets, results
from phonenumber_field.phonenumber import PhoneNumber

from xauth.models import User
from parameter import models as parameter_models
from web import mails


fields_name = {
    "label": "libellé",
    "first_name": "prénom(s)",
    "last_name": "nom(s)",
    "category": "catégorie",
    "phone": "téléphone",
    "start_at": "date de début",
    "end_at": "date de fin",
    "username": "nom d'utilisateur",
    "email": "courriel",
    "priority": "priorité",
    "is_closed": "est close",
    "is_validated": "est validé",
    "was_reopened": "a été re-ouvert",
    "is_pending": "est suspendu",
    "create_at": "enregistré le",
    "close_at": "clos le",
    "deadline": "date de rigueur",
    "is_active": "est actif",
    "author": "auteur(s)",
    "writer": "rédacteur",
    "assigned_to": "assigné à",
    "value": "valuer",
}


class PhoneNumberWidget(widgets.Widget):
    def clean(self, value, row=None, **kwargs):
        phone = PhoneNumber.from_string(str(value))

        return phone


class CustomModelResource(resources.ModelResource):
    def __init__(self, **kwargs):
        self.with_data = kwargs.pop("with_data", 1)
        super().__init__(**kwargs)

    def get_export_headers(self):
        headers = super().get_export_headers()
        if self.with_data != 1:
            return headers
        headers = [
            fields_name.get(str(header), str(header)).capitalize() for header in headers
        ]
        return headers

    def get_none(self):
        return self._meta.model.objects.none()


class UserResource(CustomModelResource):

    phone = fields.Field(
        column_name="phone", attribute="phone", widget=PhoneNumberWidget()
    )

    def before_save_instance(self, instance, row, **kwargs):
        instance.is_active = False

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "birthdate",
            "birthplace",
            "incorporation_date",
            "matricule",
            "address",
            "phone",
        ]
        export_order = [
            "id",
            "first_name",
            "last_name",
            "email",
            "birthdate",
            "birthplace",
            "incorporation_date",
            "matricule",
            "address",
            "phone",
        ]


class GroupResource(CustomModelResource):
    permissions = fields.Field(
        column_name="permissions",
        attribute="permissions",
        widget=widgets.ManyToManyWidget(auth_models.Permission, field="name"),
    )

    class Meta:
        model = auth_models.Group
        fields = ["name", "permissions"]


# parameter_fiels_import_export


class_list = [User, auth_models.Group]
resource_classes = {
    model.__name__: eval(model.__name__ + "Resource") for model in class_list
}
resource_classes.update({"default": CustomModelResource})
