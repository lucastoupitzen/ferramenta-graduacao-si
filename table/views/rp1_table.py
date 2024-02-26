import json

import openpyxl
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from table.models import *
from django.shortcuts import redirect

from .planilha_distribuicao import *
from .planilha_docentes import *
from .salvar_modificacoes import *
from .preferencias_upload import *


@login_required
def load_rp1(request):
    if request.method != "POST":
        return render(request, "table/rp1Table.html")

    excel_file = request.FILES.get("excel_file", None)

    if not excel_file:
        return redirect("page_rp1")

    if not excel_file.name.endswith(".xlsx"):
        return redirect("page_rp1")

    workbook = openpyxl.load_workbook(excel_file)
    worksheet = workbook.active

    RP1Turma.objects.filter(ano=AnoAberto.objects.get(id=1).Ano).delete()
    turmas_erro = ""

    dias_validos = ("seg", "ter", "qua", "qui", "sex")
    hrs_validos = ("08h - 12h", "14h - 18h", "19h - 22h45")

    for row in worksheet.iter_rows(min_row=3, max_col=5, values_only=True):

        dia_semana = row[2][0:3].strip()
        horario = row[2][4:].strip().lower()

        if dia_semana.lower() in dias_validos and horario in hrs_validos:
            try:
                new_rp1 = RP1Turma.objects.create(
                    codigo=row[1],
                    profs_adicionais=row[4],
                    cursos=row[3],
                    ano=AnoAberto.objects.get(id=1).Ano
                )
                DiaAulaRP1(turma_rp1=new_rp1, dia_semana=dia_semana, horario=horario).save()

            except Exception as e:
                print(e)
                return redirect("page_rp1")
        else:
            turmas_erro += f"{row[1]}, "

    return redirect("page_rp1", [turmas_erro])


@login_required
def page_rp1(request, text=""):

    rp1_turmas = RP1Turma.objects.filter(ano=AnoAberto.objects.get(id=1).Ano)
    profs_objs = Professor.objects.all()
    auto_profs = {}
    for prof_obj in profs_objs:
        auto_profs[prof_obj.NomeProf] = prof_obj.Apelido

    text = text.replace("[", "").replace("]", "").replace("'", "")

    context = {
        "rp1": rp1_turmas,
        "auto_profs": auto_profs,
        "text_erro": text
    }
    return render(request, "table/rp1Table.html", context)


@login_required
def salvar_profs_rp1(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if not is_ajax:
        return HttpResponseBadRequest('Invalid request')
    if request.method != 'POST':
        return JsonResponse({'status': 'Invalid request'}, status=400)

    data = json.load(request)
    erros = {}
    alertas = {}
    ind_modif = []
    ano = AnoAberto.objects.get(id=1).Ano
    tur = RP1Turma.objects.get(id=data["id"])
    tur.professor_si.clear()
    for prof in data["lProfs"]:
        if not prof:
            continue
        dia_aula_rp1 = DiaAulaRP1.objects.get(turma_rp1 = tur)
        # devemos adaptaros horarios e dias para serem compatíveis com as restrições
        # dicionário de correspondencia dos dias da semana
        corresp_dias_semana = {
            "Seg": 0,
            "Ter": 2,
            "Qua": 4,
            "Qui": 6,
            "Sex": 8
        }
        # dicionário de correspondencia de horário
        corresp_horarios = {
            "08h - 12h": [0,1],
            "14h - 18h": [2,4],
            "19h - 22h45": [5,7]
        }        
        prof_bd = Professor.objects.get(NomeProf=prof)
        print(corresp_horarios[dia_aula_rp1.horario])
        for horario in  corresp_horarios[dia_aula_rp1.horario]:
            data = {
                "info": {
                    'cod_disc': 'ACH0041',
                    'professor': prof_bd.Apelido,
                    'horario': horario, 
                    'dia': corresp_dias_semana[dia_aula_rp1.dia_semana], 
                    'extra': False,
                    "cod_turma": 0
                },
                "semestre": 1
            }
            aula_manha_noite(data, alertas)
            aula_noite_outro_dia_manha(data, alertas)

            if not aula_msm_horario(data["info"], ano, data, erros):
                try:
                    tur.professor_si.add(prof_bd)
                except Exception as e:
                    print("erroooo")
    print(erros)
    print(alertas)
    return JsonResponse({'erros': erros, 'alertas': alertas})