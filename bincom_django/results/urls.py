from django.urls import path
from . import views

urlpatterns = [
    path("", views.pu_result, name="pu_result"),
    path("lga-result/", views.lga_result, name="lga_result"),
    path("add-pu-result/", views.add_pu_result, name="add_pu_result"),
    # AJAX endpoints for the chained combo boxes
    path("ajax/lgas/", views.ajax_lgas, name="ajax_lgas"),          # ?state_id=
    path("ajax/wards/", views.ajax_wards, name="ajax_wards"),        # ?lga_uniqueid=
    path("ajax/polling-units/", views.ajax_polling_units, name="ajax_polling_units"),  # ?ward_uniqueid=
]
