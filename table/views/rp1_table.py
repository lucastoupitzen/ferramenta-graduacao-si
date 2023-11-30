import json
import unicodedata

import openpyxl
from django.http import HttpResponseBadRequest, JsonResponse
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

    profs_objs = Professor.objects.all()
    auto_profs = {}
    for prof_obj in profs_objs:
        auto_profs[prof_obj.NomeProf] = prof_obj.Apelido

    context = {
        "rp1": rp1_turmas,
        "auto_profs": auto_profs
    }
    return render(request, "table/rp1Table.html", context)


def salvar_profs_rp1(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if not is_ajax:
        return HttpResponseBadRequest('Invalid request')
    if request.method != 'POST':
        return JsonResponse({'status': 'Invalid request'}, status=400)

    data = json.load(request)
    tur = RP1Turma.objects.get(id=data["id"])
    tur.professor_si.clear()
    for prof in data["lProfs"]:
        if not prof:
            continue
        prof_bd = Professor.objects.get(NomeProf=prof)
        try:
            tur.professor_si.add(prof_bd)
        except Exception as e:
            print(e)
            pass

    return JsonResponse({})