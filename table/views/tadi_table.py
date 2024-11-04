import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect

from .planilha_docentes import *
from .salvar_modificacoes import *
from .preferencias_upload import *

@login_required
def page_tadi(request, text=""):

    # Defina uma ordem para os dias da semana
    order = ["8:00 - 09:45h", "10:15 - 12:00h", "14:00 - 15:45h", "16:15 - 18:00h", "19:00 - 20:45h",
                   "21:00 - 22:45h"]

    # Crie uma expressão de caso condicional para ordenar
    ordering = Case(
        *[When(diaaulatadi__horario=horario, then=Value(i)) for i, horario in enumerate(order)],
        default=Value(len(order)),
        output_field=IntegerField(),
    )

    tadi_turmas = TadiTurma.objects.filter(ano=AnoAberto.objects.get(id=1).Ano).order_by(ordering)
    profs_objs = Professor.objects.all()
    auto_profs = {}
    for prof_obj in profs_objs:
        auto_profs[prof_obj.NomeProf] = prof_obj.Apelido

    text = text.replace("[", "").replace("]", "").replace("'", "")

    context = {
        "rp1": tadi_turmas,
        "auto_profs": auto_profs,
        "text_erro": text,
        "anoAberto": AnoAberto.objects.get(id=1).Ano
    }
    return render(request, "table/tadiTable.html", context)


@login_required
def load_tadi(request):
    if request.method != "POST":
        return render(request, "table/tadiTable.html")

    excel_file = request.FILES.get("excel_file", None)

    if not excel_file:
        return redirect("page_tadi")

    if not excel_file.name.endswith(".xlsx"):
        return redirect("page_tadi")

    workbook = openpyxl.load_workbook(excel_file)
    worksheet = workbook.active

    TadiTurma.objects.filter(ano=AnoAberto.objects.get(id=1).Ano).delete()
    turmas_erro = ""

    dias_validos = ("seg", "ter", "qua", "qui", "sex")
    hrs_validos = ("8:00 - 09:45h", "10:15 - 12:00h", "14:00 - 15:45h", "16:15 - 18:00h", "19:00 - 20:45h",
                   "21:00 - 22:45h")

    for row in worksheet.iter_rows(min_row=2, max_col=3, values_only=True):

        dia_semana = row[1][0:3].strip()
        horario = row[1][4:].strip().lower()
        print(row)
        if dia_semana.lower() in dias_validos and horario in hrs_validos:
            try:
                new_tadi = TadiTurma.objects.create(
                    codigo=row[0],
                    curso=row[2],
                    ano=AnoAberto.objects.get(id=1).Ano
                )
                DiaAulaTadi(turma_tadi=new_tadi, dia_semana=dia_semana, horario=horario).save()

            except Exception as e:
                print(e)
                return redirect("page_tadi")
        else:
            turmas_erro += f"{row[0]}, "

    return redirect("page_tadi", [turmas_erro])


@login_required
def save_prof_tadi(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if not is_ajax:
        return HttpResponseBadRequest('Invalid request')
    if request.method != 'POST':
        return JsonResponse({'status': 'Invalid request'}, status=400)

    data = json.load(request)

    erros = {}
    alertas = {}
    print(data)

    ano = AnoAberto.objects.get(id=1).Ano
    tur = TadiTurma.objects.get(id=data["id"])
    tur.professor_si.clear()

    if data["lProfs"] == ['']:
        return JsonResponse({'status': 'String vazia'})

    dia_aula_tadi = DiaAulaTadi.objects.get(turma_tadi = tur)
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
        "8:00 - 09:45h": 0,
        "10:15 - 12:00h": 1,
        "14:00 - 15:45h": 2,
        "16:15 - 18:00h": 4,
        "19:00 - 20:45h": 5,
        "21:00 - 22:45h": 7
    }

    prof_bd = Professor.objects.get(NomeProf=data["lProfs"][0])

    data = {
        "info": {
            'cod_disc': 'ACH0021',
            'professor': prof_bd.Apelido,
            'horario': corresp_horarios[dia_aula_tadi.horario],
            'dia': corresp_dias_semana[dia_aula_tadi.dia_semana],
            'extra': False,
            "cod_turma": 0
        },
        "semestre": 1
    }
    aula_manha_noite(data, alertas, ano)
    aula_noite_outro_dia_manha(data, alertas, ano)

    if not aula_msm_horario(data["info"], ano, data, erros):
        try:
            tur.professor_si.add(prof_bd)
        except Exception as e:
            print("erroooo")

    print(erros)
    print(alertas)

    return JsonResponse({'erros': erros, 'alertas': alertas})