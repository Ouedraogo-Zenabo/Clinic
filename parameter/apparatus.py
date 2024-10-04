from django.forms import fields, forms
from formset.collection import FormCollection
from formset.renderers.bootstrap import FormRenderer
from formset.views import FormCollectionView

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