import json

import openpyxl
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from ..models import *
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
        return redirect("ferramenta_graduacao_si:page_rp1")

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
    rest_turno = {"manha": 0, "tarde": 22, "noite": 48}
    dia_sem = {"segunda": 0, "terca": 2, "quarta": 4, "quinta": 6, "sexta": 8}
    auto_profs = {}
    restricoes_profs = {}
    impedimentos_totais = {}
    for prof_obj in profs_objs:
        auto_profs[prof_obj.NomeProf] = prof_obj.Apelido
        restricoes = prof_obj.restricao_set.filter(semestre="1")

        restricoes_profs[str(prof_obj.Apelido)] = []
        impedimentos_totais[str(prof_obj.Apelido)] = []

        for rest_prof in restricoes:
            list_rest_indice = []
            indice = dia_sem[rest_prof.dia] + rest_turno[rest_prof.periodo]
            if rest_prof.periodo == "tarde" and rest_prof.dia == "segunda":
                list_rest_indice = [indice, 23, 33, 34, 35, 36]
            elif rest_prof.periodo == "tarde":
                list_rest_indice = [indice, indice + 1, indice + 13, indice + 14]
            elif rest_prof.periodo == "noite":
                indice = indice - 2
                list_rest_indice = [
                    indice,
                    indice + 1,
                    indice + 11,
                    indice + 12,
                    indice + 22,
                    indice + 23,
                    indice + 33,
                    indice + 34,
                ]
            else:
                list_rest_indice = [indice, indice + 1, indice + 11, indice + 12]

            if str(prof_obj.Apelido) in restricoes_profs:
                restricoes_profs[str(prof_obj.Apelido)] += list_rest_indice
            else:
                restricoes_profs[str(prof_obj.Apelido)] = list_rest_indice

            # impedimento total
            if rest_prof.impedimento:
                impedimentos_totais[str(prof_obj.Apelido)] = list_rest_indice

    text = text.replace("[", "").replace("]", "").replace("'", "")

    context = {
        "rp1": rp1_turmas,
        "auto_profs": auto_profs,
        "text_erro": text,
        "anoAberto": AnoAberto.objects.get(id=1).Ano,
        "impedimentos_totais": impedimentos_totais,
        "rest_horarios": restricoes_profs
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
        erro_caso = {}
        alerta_caso = {}
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
        for horario in corresp_horarios[dia_aula_rp1.horario]:

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
            aula_manha_noite(data, alerta_caso, ano)
            aula_noite_outro_dia_manha(data, alerta_caso, ano)
            print("Atenção aqui")
            print(aula_msm_horario(data["info"], ano, data, erro_caso))
            print("do professor " + data["info"]["professor"])
            if not aula_msm_horario(data["info"], ano, data, erro_caso):
                try:
                    tur.professor_si.add(prof_bd)
                except Exception as e:
                    print("erroooo")
            else: 
                alertas[prof] = alerta_caso
                erros[prof] = erro_caso
                break
            
            alertas[prof] = alerta_caso
            erros[prof] = erro_caso

    print(erros)
    print(alertas)
    return JsonResponse({'erros': erros, 'alertas': alertas})