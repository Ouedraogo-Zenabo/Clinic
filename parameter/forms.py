from django.forms import forms, fields, widgets
from django.forms.models import ModelForm, ModelChoiceField
from django.db.models import Q
from formset.collection import FormCollection
from formset.renderers.bootstrap import FormRenderer
from formset.views import FormCollectionView
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



class ChemistryForm(forms.Form):
    ph_value = fields.FloatField(
        label="pH value",
        initial=7.0,
        min_value=0.0,
        max_value=14.0,
        step_size=0.1,
    )

class ElectricityForm(forms.Form):
    resistance = fields.IntegerField(
        label="Resistance in Ω",
        min_value=1,
        initial=100,
    )

class ApparatusCollection(FormCollection):
    default_renderer = FormRenderer(field_css_classes='mb-3')
    substance = ChemistryForm()
    conductivity = ElectricityForm()

class ApparatusView(FormCollectionView):
    collection_class = ApparatusCollection
    template_name = "form-collection.html"
    success_url = "/success"