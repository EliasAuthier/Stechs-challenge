from django.urls import path

from . import views

urlpatterns = [
    path("device/inventory/cm/<str:cm_address>", views.cm_data, name="index"),
]