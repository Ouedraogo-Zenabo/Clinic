from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from web.views import (
    CustomCreateView,
    CustomDeleteView,
    CustomDetailView,
    CustomListView,
    CustomUpdateView,
    CustomFormCollectionView
)

from parameter.models import Clinic
from parameter.forms import ClinicForm
from parameter.models import Pharmacie
from parameter.forms import PharmacieForm
from parameter.models import Apparatus
from parameter.forms import ApparatusCollection

# Create your views here.


class ClinicListView(CustomListView):
    model = Clinic
    name = "clinic"
    template_name = "list-parameter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_delete"] = False

        return context
    
class PharmacieListView(CustomListView):
    model = Pharmacie 
    name = "pharmacie"
    template_name = "list-parameter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_delete"] = False

        return context


class ClinicCreateView(CustomCreateView):
    model = Clinic
    form_class = ClinicForm
    name = "clinic"
    success_url = reverse_lazy("parameter:clinic-list")

class PharmacieCreateView(CustomCreateView):
    model = Pharmacie
    form_class = PharmacieForm
    name = "pharmacie"
    success_url = reverse_lazy("parameter:pharmacie-list")

class ClinicDetailView(CustomDetailView):
    model = Clinic
    name = "clinic"
    template_name = "detail-parameter.html"
    
class PharmacieDetailView(CustomDetailView):
    model = Pharmacie
    name = "Pharmacie"
    template_name = "detail-parameter.html"

class ClinicUpdateView(CustomUpdateView):
    model = Clinic
    name = "clinic"
    form_class = ClinicForm
    success_url = reverse_lazy("parameter:clinic-list")
    

class PharmacieUpdateView(CustomUpdateView):
    model = Pharmacie
    name = "pharmacie"
    form_class = PharmacieForm
    success_url = reverse_lazy("parameter:pharmacie-list")





class ClinicDeleteView(CustomDeleteView):
    model = Clinic
    name = "clinic"


class ApparatusView(CustomFormCollectionView):
    model = Apparatus
    name = "apparatus"
    collection_class = ApparatusCollection
    success_url = reverse_lazy("parameter:apparatus-list")


class ApparatusListView(CustomListView):
    model = Apparatus 
    name = "apparatus"
    template_name = "list-collection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_delete"] = False

        return context