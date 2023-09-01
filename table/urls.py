from django.urls import path
from .views import *

urlpatterns = [
    path("table/<int:semestre>/", views.index, name="table"),
    path("table", views.index, name="table"),
    path("save_modify", views.save_modify, name="save_modify"),
    path(
        "download_excel_data",
        views.download_excel_data,
        name="download_excel_data",
    ),
    path("", views.menu, name="menupage"),
    path("redirect", views.redirect, name="redirect"),
    path("process_file", views.pref_planilha, name="process_file")
]
