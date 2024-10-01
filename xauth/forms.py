from datetime import timedelta, date

# from typing import Any
from django.forms import forms, fields, widgets
from django.forms.models import ModelForm, ModelChoiceField
from django.db.models import Q
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from formset.collection import FormMixin, FormCollection
from formset.widgets import (
    Selectize,
    DualSortableSelector,
    UploadedFileInput,
    DateInput,
)
from formset.utils import FormsetErrorList
from formset.renderers.bootstrap import FormRenderer
from django.conf import settings

from web.constants import MEDIUM_LENGTH, MIN_LENGTH, submit
from parameter import models as params_models

from xauth.models import User, Assign, AccountActivationSecret


MINIMUM_AGE = 18 * 365

default_renderer = FormRenderer(
    form_css_classes="row",
    field_css_classes={"*": "mb-2 col-md-6 input100"},
)


class GroupForm(FormMixin, ModelForm):
    default_renderer = FormRenderer(
        form_css_classes="row",
        field_css_classes={"*": "mb-2 col-md-12 input100"},
    )

    def __init__(self, error_class=FormsetErrorList, **kwargs):
        super().__init__(error_class, **kwargs)
        permissions = Permission.objects.filter(
            content_type__app_label__in=[
                "xauth",
                "auth",
                "parameter",
            ]
        )
        permissions = permissions.exclude(
            content_type__model__in=[
                "assign",
                "accountactivationsecret",
                "historicalassign",
            ]
        )
        self.fields["permissions"].queryset = permissions

    class Meta:
        model = Group
        fields = "__all__"
        widgets = {
            "permissions": DualSortableSelector(
                search_lookup=["name__icontains"],
                group_field_name="content_type",
            )
        }


class CustomSetPasswordForm(FormMixin, SetPasswordForm):
    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.is_active = True
        self.user.save()

        return self.user


class UserCreateForm(FormMixin, ModelForm):
    default_renderer = FormRenderer(
        form_css_classes="row",
        field_css_classes={
            "*": "mb-3 col-md-6",
            "photo": "mb-5 col-md-6",
            "folder": "mb-5 col-md-6",
            "is_military": "mx-5 mb-5 col-md-12",
        },
    )

    is_military = fields.ChoiceField(
        choices=(("oui", "Oui"), ("non", "Non")),
        widget=widgets.RadioSelect,
        label="Est un militaire",
    )

    def clean_incorporation_date(self):
        incorporation_date: date = self.cleaned_data.get("incorporation_date")
        diff_age = date.today() - incorporation_date

        if diff_age.days < MINIMUM_AGE:
            raise forms.ValidationError(
                "Ce soldat n'a pa encore l'age d'intégré l'armée"
            )

        return incorporation_date

    def clean_engagement_date(self):
        engagement_date: date = self.cleaned_data.get("engagement_date")
        diff_age = date.today() - engagement_date

        if diff_age.days < MINIMUM_AGE:
            raise forms.ValidationError(
                "Ce soldat n'a pa encore l'age d'intégré l'armée"
            )

        return engagement_date

    def clean_promotion_date(self):
        promotion_date: date = self.cleaned_data.get("promotion_date")
        diff_age = date.today() - promotion_date

        if diff_age.days < MINIMUM_AGE:
            raise forms.ValidationError(
                "Ce soldat n'a pa encore l'age d'intégré l'armée"
            )

        return promotion_date

    def __init__(self, error_class=FormsetErrorList, user: User = None, **kwargs):
        super().__init__(error_class, **kwargs)
        if user:
            if user.is_staff:
                self.fields["structure"].queryset = (
                    params_models.Structure.available_objects.filter(level=5)
                )
                self.fields["company"].queryset = (
                    params_models.Structure.available_objects.filter(level=6)
                )
            elif hasattr(user, "assign"):
                self.fields["structure"].queryset = (
                    user.assign.structure.get_children().filter(level=5)
                )
                self.fields["company"].queryset = (
                    user.assign.structure.get_children().filter(level=6)
                )
                if user.assign.structure.level in [1, 2, 3]:
                    self.fields["army"].queryset = (
                        user.assign.structure.get_children().filter(level=3)
                    )
                    self.fields["region"].queryset = (
                        user.assign.structure.get_children().filter(level=4)
                    )
                elif user.assign.structure.level in [4]:
                    self.fields[
                        "army"
                    ].queryset = user.assign.structure.get_ancestors().filter(
                        pk=user.assign.structure.parent.pk
                    )
                    self.fields["region"].queryset = (
                        user.assign.structure.get_children().filter(level=4)
                    )
                elif user.assign.structure.level in [5]:
                    self.fields[
                        "army"
                    ].queryset = user.assign.structure.get_ancestors().filter(
                        pk=user.assign.structure.parent.parent.pk
                    )
                    self.fields[
                        "region"
                    ].queryset = user.assign.structure.get_ancestors().filter(
                        pk=user.assign.structure.parent.pk
                    )
                else:
                    self.fields["structure"].queryset = (
                        params_models.Structure.available_objects.none()
                    )
            else:
                self.fields["structure"].queryset = (
                    params_models.Structure.available_objects.none()
                )

        else:
            self.fields["structure"].queryset = (
                params_models.Structure.available_objects.none()
            )

    def clean(self):
        cleaned_data = super().clean()
        is_military = cleaned_data.get("is_military")

        if is_military:
            mandatory_fields = [
                "incorporation_date",
                "engagement_date",
            ]
            errors = {}
            error_message = "Ce champ est obligatoire"

            for field in mandatory_fields:
                if not cleaned_data.get(field):
                    errors[field] = error_message

        if errors:
            raise forms.ValidationError(errors, code="mandatory_field")

        return cleaned_data

    def clean__gender(self):
        gender = self.cleaned_data["gender"]

        if not gender:
            raise forms.ValidationError(
                "Ce champ est obligatoire", code="mandatory_field"
            )

        return gender

    def clean__marital_status(self):
        marital_status = self.cleaned_data["marital_status"]

        if not marital_status:
            raise forms.ValidationError(
                "Ce champ est obligatoire", code="mandatory_field"
            )

        return marital_status

    class Meta:
        model = User
        fields = [
            "photo",
            "folder",
            "is_military",
            "first_name",
            "last_name",
            "birthdate",
            "birthplace",
            "email",
            "matricule",
            "address",
            "phone",
            "incorporation_date",
            "engagement_date",
            "promotion_date",
        ]
        widgets = {
            "birthdate": DateInput,
            "incorporation_date": DateInput,
            "engagement_date": DateInput,
            "promotion_date": DateInput,
            "photo": UploadedFileInput(attrs={"max-size": 1024 * 1024 * 3}),
            "folder": UploadedFileInput(
                attrs={
                    "max-size": 1024 * 1024 * 5,
                    "df-show": ".is_military=='oui'",
                }
            ),
        }
        labels = {
            "email": "Adresse email",
            "address": "Adresse",
        }


class UserChangeForm(FormMixin, ModelForm):
    default_renderer = default_renderer

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "birthdate",
            "birthplace",
            "email",
            "matricule",
            "address",
            "phone",
            "incorporation_date",
            "engagement_date",
            "promotion_date",
        ]
        widgets = {
            "birthdate": DateInput,
            "incorporation_date": DateInput,
            "engagement_date": DateInput,
            "promotion_date": DateInput,
        }
        labels = {"email": "Adresse email"}


class UserConfirmDeleteForm(forms.Form):
    default_renderer = default_renderer
    matricule = fields.CharField(max_length=MIN_LENGTH)

    def __init__(self, error_class=FormsetErrorList, user=None, **kwargs):
        super().__init__(error_class, **kwargs)
        self.user = user

    def clean_matricule(self):
        matricule = self.cleaned_data.get("matricule")
        if matricule != self.user.matricule:
            raise forms.ValidationError("Le matricule ne correspond pas!")
        return matricule


class UserChangeProfilePhotoForm(FormMixin, ModelForm):
    default_renderer = default_renderer

    class Meta:
        model = User
        fields = ("photo",)
        widgets = {"photo": UploadedFileInput(attrs={"max-size": 1024 * 1024 * 3})}


class UserPublicActivationForm(FormMixin, forms.Form):
    identifier = fields.CharField(
        max_length=MIN_LENGTH,
        label="Identifiant",
        help_text="Vous pouvez saisir soit votre email ou votre matricule",
    )
    secret = fields.CharField(
        max_length=MIN_LENGTH,
        label="Code secret",
        help_text="Il s'agit du code que vous avez reçu par mail/sms",
    )

    default_renderer = default_renderer

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data["identifier"]
        secret = cleaned_data["secret"]

        user = User.objects.filter(Q(matricule=identifier) | Q(email=identifier))

        if not user.exists():
            raise forms.ValidationError(
                "Les informations fournies ne correspondent pas à un compte.",
                code="mismatch_account",
            )

        user = user.first()
        if user.is_active:
            raise forms.ValidationError(
                "Les informations fournies ne correspondent pas à un compte.",
                code="mismatch_account",
            )

        exist = AccountActivationSecret.available_objects.filter(
            user=user, secret=secret
        ).exists()
        if not exist:
            raise forms.ValidationError(
                "Les informations fournies ne correspondent pas à un compte.",
                code="mismatch_account",
            )
        cleaned_data["user"] = user
        return cleaned_data


class AssignForm(FormMixin, ModelForm):
    default_renderer = default_renderer

    def __init__(self, error_class=FormsetErrorList, **kwargs):
        super().__init__(error_class, **kwargs)
        if "instance" in kwargs and kwargs["instance"] is not None:
            # self.fields["code"].widget.attrs["readonly"] = True
            pass

    class Meta:
        model = Assign
        fields = ["group_assign", "nomination_date", "effective_date"]
        widgets = {
            "nomination_date": DateInput,
            "effective_date": DateInput,
            "office": Selectize(
                search_lookup="label__icontains",
                placeholder="Choisir le poste",
            ),
        }


class RoleForm(FormMixin, ModelForm):
    default_renderer = default_renderer

    #
    def __init__(self, error_class=FormsetErrorList, user: User = None, **kwargs):
        super().__init__(error_class, **kwargs)
        if "instance" in kwargs and kwargs["instance"] is not None:
            # self.fields["structure"].widget.attrs["readonly"] = True
            pass

    class Meta:
        model = Assign
        fields = [
            "group_assign",
        ]
        widgets = {
            "group_assign": Selectize(
                search_lookup="label__icontains",
                placeholder="Choisir le rôle",
            ),
        }
        labels = {
            "group_assign": "Rôle",
        }
