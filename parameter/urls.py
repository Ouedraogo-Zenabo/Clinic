from django.urls import path

from parameter import views

app_name = "parameter"

urlpatterns = [
    path(
        "parameters/clinics/list/",
        view=views.ClinicListView.as_view(),
        name="clinic-list",
    ),
     path(
        "parameters/pharmacie/list/",
        view=views.PharmacieListView.as_view(),
        name="pharmacie-list",
    ),
    
    path(
        "parameters/clinics/create/",
        view=views.ClinicCreateView.as_view(),
        name="clinic-create",
    ),
     path(
        "parameters/pharmacie/create/",
        view=views.PharmacieCreateView.as_view(),
        name="pharmacie-create",
    ),
    
    path(
        "parameters/clinics/<slug:slug>/detail/",
        view=views.ClinicDetailView.as_view(),
        name="clinic-detail",
    ),
    
    path(
        "parameters/pharmacie/<slug:slug>/detail/",
        view=views.PharmacieDetailView.as_view(),
        name="pharmacie-detail",
    ), 
    
    path(
        "parameters/clinics/<slug:slug>/update/",
        view=views.ClinicListView.as_view(),
        name="clinic-update",
    ),
    
     path(
        "parameters/pharmacie/<slug:slug>/update/",
        view=views.PharmacieListView.as_view(),
        name="pharmacie-update",
    ),
    
    path(
        "parameters/clinics/<slug:slug>/delete/",
        view=views.ClinicListView.as_view(),
        name="clinic-delete",
    ),
]
