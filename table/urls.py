from django.urls import path, include
from .views import *

urlpatterns = [
    path("table/<int:semestre>/<int:ano>/", views.index, name="table"),
    path("save_modify", views.save_modify, name="save_modify"),
    path("save_p", rp1_table.salvar_profs_rp1, name="save_p"),
    path(
        "download_zip_planilhas",
        views.download_zip_planilhas,
        name="download_zip_planilhas",
    ),
    path("", views.menu, name="menupage"),
    path("load_rp1", rp1_table.load_rp1, name="load_rp1"),
    path("page_rp1", rp1_table.page_rp1, name="page_rp1"),
    path('page_rp1/<str:text>/', rp1_table.page_rp1, name='page_rp1'),
    path("redirect", views.redirect, name="redirect"),
    path("process_file", views.pref_planilha, name="process_file")
    #path("login/", include("django.contrib.auth.urls")),
    #path("login/", include("login.urls"))
]
