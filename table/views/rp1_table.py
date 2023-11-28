import openpyxl
from django.shortcuts import render
from table.models import *


def load_rp1(request):
    if request.method == "POST":
        excel_file = request.FILES.get("excel_file", None)

        if not excel_file:
            return render(
                request, "table/rp1Table.html", {"error_message": "Nenhum arquivo enviado."}
            )

        if not excel_file.name.endswith(".xlsx"):
            return render(
                request,
                "table/rp1Table.html",
                {
                    "error_message": "Formato de arquivo inválido. Por favor, envie um arquivo do tipo .xlsx."
                },
            )

        try:
            workbook = openpyxl.load_workbook(excel_file)
            worksheet = workbook.active

            RP1Turma.objects.filter(ano=AnoAberto.objects.get(id=1).Ano).delete()

            for row in worksheet.iter_rows(min_row=3, max_col=5, values_only=True):
                new_rp1 = RP1Turma.objects.create(
                    codigo=row[1],
                    profs_adicionais=row[4],
                    cursos=row[3],
                    ano=AnoAberto.objects.get(id=1).Ano
                )
                new_rp1.save()
                dia_semana = row[2][0:3].strip()
                horario = row[2][4:].strip()
                DiaAulaRP1(turma_rp1=new_rp1, dia_semana=dia_semana, horario=horario).save()

                # print(f"{new_rp1.codigo}, {new_rp1.profs_adicionais}, {new_rp1.cursos}, {new_rp1.ano}")
                #print(f"{horario}, {dia_semana}")

            return render(
                request,
                "table/rp1Table.html",
                {"success_message": "Dados de preferência salvos com sucesso."},
            )

        except Exception as e:
            print(e)
            return render(
                request,
                "table/rp1Table.html",
                {"error_message": "Ocorreu um erro ao processar o arquivo."},
            )

    return render(request, "table/rp1Table.html")


def page_rp1(request):
    rp1_turmas = RP1Turma.objects.filter(ano=AnoAberto.objects.get(id=1).Ano)

    return render(request, "table/rp1Table.html", {"rp1": rp1_turmas})