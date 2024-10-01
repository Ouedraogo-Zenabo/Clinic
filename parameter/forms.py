from django.forms import forms, fields, widgets
from django.forms.models import ModelForm, ModelChoiceField
from django.db.models import Q

from formset.collection import FormMixin, FormCollection
from formset.widgets import (
    Selectize,
    DualSortableSelector,
    UploadedFileInput,
    DateInput,
)
from formset.richtext.widgets import RichTextarea
from formset.utils import FormsetErrorList
from formset.renderers.bootstrap import FormRenderer
from django.conf import settings

from parameter.models import Clinic
from parameter.models import Pharmacie
from web.constants import control_elements, TEXTAREA

default_renderer = FormRenderer(
    form_css_classes="row",
    field_css_classes={
        "*": "mb-2 col-md-6 input100",
        "description": "mb-2 col-md-12 input100",
    },
)


class ClinicForm(FormMixin, ModelForm):
    default_renderer = default_renderer

    class Meta:
        model = Clinic
        fields = ["code", "label", "address", "description"]
        widgets = {
            "description": RichTextarea(
                control_elements=control_elements, attrs=TEXTAREA
            ),
        }


class PharmacieForm(FormMixin, ModelForm):
    default_renderer = default_renderer

    class Meta:
        model = Pharmacie
        fields = ["code", "label", "address", "description"]
        widgets = {
            "description": RichTextarea(
                control_elements=control_elements, attrs=TEXTAREA
            ),
        }
