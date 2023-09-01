import openpyxl
from table.models import *
from django.db.models import Prefetch
from datetime import datetime
from openpyxl.styles import PatternFill, Font


def planilha_docentes(sheet_doc):
    # carregando os dados na memória
    turma_prefetch = Prefetch(
        "turma_set",
        queryset=Turma.objects.filter(Ano=datetime.now().year).select_related("CoDisc"),
    )
    profs = (
        Professor.objects.all().prefetch_related(turma_prefetch).order_by("NomeProf")
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