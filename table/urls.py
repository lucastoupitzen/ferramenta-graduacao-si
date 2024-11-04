from django.urls import path, include
from .views import *
from .views import tadi_table

urlpatterns = [
    path("table/<int:semestre>/<int:ano>/", views.index, name="table"),
    path("save_modify", views.save_modify, name="save_modify"),
    path(
        "download_zip_planilhas",
        views.download_zip_planilhas,
        name="download_zip_planilhas",
    ),
    path("", views.menu, name="menupage"),
    path("redirect", views.redirect, name="redirect"),
    path("process_file", views.pref_planilha, name="process_file"),
    

    # página rp1
    path("load_rp1", rp1_table.load_rp1, name="load_rp1"),
    path("page_rp1", rp1_table.page_rp1, name="page_rp1"),
    path('page_rp1/<str:text>/', rp1_table.page_rp1, name='page_rp1'),
    path("save_p", rp1_table.salvar_profs_rp1, name="save_p"),

    # página TADI
    path("load_tadi", tadi_table.load_tadi, name="load_tadi"),
    path("page_tadi", tadi_table.page_tadi, name="page_tadi"),
    path('page_tadi/<str:text>/', tadi_table.page_tadi, name='page_tadi'),
    path("save_tadi", tadi_table.save_prof_tadi, name="save_tadi"),
    
    #atribuição
    path("load_atribuicao", views.carregar_atribuicao, name="load_atribuicao"),
    path("gerar_atribuicao", views.criar_atribuicoes, name="gerar_atribuicao"),
]
