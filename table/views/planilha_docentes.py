#FUNÇÕES PARA ATRIBUIÇÃO AUTOMÁTICA
import os
import openpyxl
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from openpyxl.reader.excel import load_workbook
from unidecode import unidecode

from table.models import *
from django.db.models import Prefetch
from datetime import datetime
from openpyxl.styles import PatternFill, Font


def planilha_docentes(sheet_doc):
    # carregando os dados na memória
    turma_prefetch = Prefetch(
        "turma_set",
        queryset=Turma.objects.filter(AnoAberto.objects.get(id=1).Ano).select_related("CoDisc"),
    )
    profs = (
        Professor.objects.filter(em_atividade=True).prefetch_related(turma_prefetch).order_by("NomeProf")
    )

    row = 3
    for professor in profs:
        col_1_disc = 2
        col_2_disc = 8
        hrs_aula_1 = 0
        hrs_aula_2 = 0

        # Precisa cuidar do caso do optativaCB
        for turma in professor.turma_set.all():
            if turma.CoDisc.TipoDisc == "optativaCB":
                continue
            if turma.CoDisc.SemestreIdeal % 2:
                # Impar
                hrs_aula_1 += preenche_doc(sheet_doc, row, col_1_disc, turma)
                col_1_disc += 1
            else:
                hrs_aula_2 += preenche_doc(sheet_doc, row, col_2_disc, turma)
                col_2_disc += 1

        sheet_doc.cell(row=row, column=1).value = professor.NomeProf
        # Preenche os créditos aula
        sheet_doc[f"V{row}"].value = hrs_aula_1
        sheet_doc[f"W{row}"].value = hrs_aula_2
        sheet_doc[f"X{row}"].value = hrs_aula_2 + hrs_aula_1

        row += 1


def preenche_doc(sheet_doc, row, col, turma):
    disciplina = turma.CoDisc
    if turma.Eextra == "S":
        sheet_doc.cell(row=row, column=col).font = Font(
            color="FF0000", size=10, name="Calibri"
        )

    if disciplina.TipoDisc.lower() != "obrigatoria":
        sheet_doc.cell(row=row, column=col).fill = openpyxl.styles.PatternFill(
            start_color="008000", end_color="008000", fill_type="solid"
        )

    sheet_doc.cell(
        row=row, column=col
    ).value = f"{str(disciplina.CoDisc)}-{str(disciplina.Abreviacao)}"

    return disciplina.CreditosAula
#
# def escolhe_profs_disc(pref):
#     #query do histórico
#
#
#     #print(anos_consulta)
#
# def criar_atribuicoes():
#     profs = Professor.objects.filter(em_atividade=True).order_by('NomeProf')
#     discs = Disciplina.objects.filter(ativa=True, TipoDisc="obrigatoria")
#     ano_atual = int(AnoAberto.objects.get(id=1).Ano)
#     anos_consulta = [_ for _ in range(2015, ano_atual)]
#     for disc in discs:
#         print(disc)
#         pref_disc = disc.preferencias_set.filter(AnoProf=2024)
#         num_pref = pref_disc.count()
#         # print(pref_disc.filter(nivel=1))
#         prof_02 = prof_04 = prof_94 = ""
#
#         if num_pref > 3:
#             #escolher três profs com o histórico de vezes ministradas e período
#
#         elif num_pref < 3:
#             pass
#         else:
#             pass
#
#         print()
#
# def ler_atribuicao():
#     cwd = os.getcwd()
#     file_path = os.path.join(cwd, "table/static/table/atribuicoes/at_2023.xlsx")
#     source_workbook = load_workbook(filename=file_path)
#     sheet_doc = source_workbook["docentes"]
#     profs = Professor.objects.all()
#
#     for row in sheet_doc.iter_rows(min_row=3, max_row=41, max_col=11, values_only=True):
#
#         prof_excel = row[0].lower().replace(" ", "")
#         prof_encontrado = False
#         prof_obj = ""
#
#         # Adicione aqui os nomes certos do bd
#         nao_encontrado_db = {
#             "andreaquino": "André Carlos Busanelli de Aquino",
#             "josédejesuspérezalcazár": "José de Jesús Pérez-Alcázar",
#             "lucianemeneguinortegavidal": "Luciane Meneguin Ortega"
#         }
#
#         if prof_excel in nao_encontrado_db:
#             prof_obj = Professor.objects.get(NomeProf=nao_encontrado_db[prof_excel])
#             prof_encontrado = True
#         else:
#             # sem considerar eficiência
#             for prof in profs:
#                 if unidecode(prof_excel) == unidecode(prof.NomeProf.lower().replace(" ", "")):
#                     prof_obj = prof
#                     prof_encontrado = True
#                     break
#
#         if not prof_encontrado:
#             print(f"professor: {prof_excel}, não encontrado!")
#             continue
#
#         # cria disciplina para o professor
#         for disciplina in row[1:]:
#             codisc_db = ""
#
#             if disciplina is None or not isinstance(disciplina, str):
#                 continue
#
#             try:
#                 codisc = disciplina.split("-")[0]
#                 codisc_db = Disciplina.objects.get(CoDisc=codisc)
#
#             except ObjectDoesNotExist:
#                 print(f"disciplina {disciplina} não encontrada para o professor: {prof_obj.Apelido}")
#                 continue
#
#             if codisc_db.TipoDisc != "obrigatoria":
#                 continue
#
#             try:
#                 nova_turma = Turma.objects.create(
#                     CoDisc=codisc_db,
#                     # Código arbitrário
#                     CodTurma=99,
#                     # COLOQUE O ANO DA PLANILHA
#                     Ano=2025,
#                     NroUSP=prof_obj,
#                     Eextra="N",
#                     SemestreAno="P"
#                 )
#                 print(nova_turma)
#
#             except IntegrityError:
#                 pass
#
#             print("\n")
