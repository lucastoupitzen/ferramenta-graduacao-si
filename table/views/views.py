import os
import zipfile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
from openpyxl.reader.excel import load_workbook
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import unicodedata
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from .planilha_distribuicao import *
from .planilha_docentes import *
from .salvar_modificacoes import *
from .preferencias_upload import *

@login_required
def index(request, semestre, ano):
    # cria listas com referências diferentes
    # elas serão iteradas no index.html para carregar os dados na planilha editável
    tbl_vls = [[""] * 10 for _ in range(8)]
    tbl_vls.insert(3, ["", ""])

    tbl_extra = [[""] * 10 for _ in range(4)]

    query_smt = [7, 8] if semestre in [7, 8] else [semestre]
    smt_ano = "I" if semestre % 2 else "P"
    vls_turmas = Turma.objects.filter(
        Q(CoDisc__SemestreIdeal__in=query_smt, Ano=ano, SemestreAno=smt_ano, Eextra="N") |
        Q(Ano=ano, Eextra="S", SemestreAno=smt_ano, semestre_extra=semestre)
    )
    turmas_rp_db = Turmas_RP.objects.all()

    for tur_materia in vls_turmas:
        cod_disc = tur_materia.CoDisc
        if str(cod_disc) == "ACH0042":
            prof = []
            for turma_rp in turmas_rp_db:
                if(turma_rp.turma.CodTurma == tur_materia.CodTurma):
                    prof.append(turma_rp.professor.Apelido)
            prof = " / ".join(prof)
        else: prof = tur_materia.NroUSP.Apelido
        t_nro = int(tur_materia.CodTurma)
        t_extra = tur_materia.Eextra

        # faz a uma consulta na relação N:N
        dias_aulas = tur_materia.dia_set.all()

        for dia in dias_aulas:

            col_tbl = int(dia.DiaSemana)
            row_tbl = int(dia.Horario)

            if row_tbl in (5, 7) and t_nro == 94:
                row_tbl += 1

            # caso do vespertino 1 com duas linhas
            # 33 é um número arbitrário
            if t_nro == 33:
                row_tbl += 1

            if t_extra == "S" and row_tbl not in (2, 3, 4):
                if row_tbl == 5:
                    row_tbl = 2
                elif row_tbl == 7:
                    row_tbl = 3
                atribuir_tbl_values(tbl_extra, cod_disc, row_tbl, col_tbl, prof)
            else:
                atribuir_tbl_values(tbl_vls, cod_disc, row_tbl, col_tbl, prof)

    rest_turno = {"manha": 0, "tarde": 22, "noite": 48}
    dia_sem = {"segunda": 0, "terca": 2, "quarta": 4, "quinta": 6, "sexta": 8}
    profs_objs = Professor.objects.all()
    restricoes_profs = {}
    impedimentos_totais = {}

    # Decide quais restrições serão carregadas
    s_rest = "1" if semestre % 2 else "2"

    auto_profs = {}  # para o autocomplete do nome do professor com apelido
    detalhes_profs = {}
    for prof_obj in profs_objs:
        # Já carrega dados necessários para as sugestões e detalhes do professor
        nome = unicodedata.normalize("NFD", prof_obj.NomeProf.lower())
        auto_profs[prof_obj.NomeProf] = prof_obj.Apelido
        consideracao = prof_obj.consideracao1 if semestre % 2 else prof_obj.consideracao2
        detalhes_profs[nome] = [prof_obj.NomeProf, prof_obj.Apelido, prof_obj.pos_doc, prof_obj.pref_optativas,
                                consideracao]

        # tentar melhorar desempenho da linha abaixo
        restricoes = prof_obj.restricao_set.filter(semestre=s_rest)

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

    discs = Disciplina.objects.all()
    cods_tbl_hr = {}
    cods_tbl_hr_ext = {}  # códigos para preencher a tabela de matérias que não são do semestre selecionado
    mtr_auto_nome = {}  # auxilia no autocomplete para encontrar o código da turma extra

    for disc in discs:

        if disc.SemestreIdeal == semestre or \
                (semestre in [8, 7] and disc.TipoDisc == "optativaSI"):
            cods_tbl_hr[f"{disc.CoDisc} {disc.Abreviacao}"] = disc.CoDisc

        else:
            cods_tbl_hr_ext[f"{disc.CoDisc} {disc.Abreviacao}"] = disc.CoDisc
            mtr_auto_nome[disc.NomeDisc] = f"{disc.CoDisc} {disc.Abreviacao}"

    # Serve para listar as disciplinas na página
    if semestre in [7, 8]:
        vls_disciplinas = discs.filter(Q(SemestreIdeal=semestre) | Q(TipoDisc="optativaSI"))
    else:
        vls_disciplinas = discs.filter(SemestreIdeal=semestre)

    disc_obrig = vls_disciplinas.filter(TipoDisc="obrigatoria")
    tables_info = [
        {
            "title": "Disciplinas SI (Obrigatórias)",
            "mtrs": disc_obrig,
        },
        {
            "title": "Disciplinas SI (Optativas CB)",
            "mtrs": vls_disciplinas.filter(TipoDisc="optativaCB"),
        },
        {
            "title": "Disciplinas SI (Optativas SI)",
            "mtrs": vls_disciplinas.filter(TipoDisc="optativaSI"),
        },
    ]

    # prepara os dados para tabela de preferencias
    pref_semestre = Preferencias.objects.filter(
        CoDisc__SemestreIdeal=semestre
    ).order_by("CoDisc__Abreviacao")
    tbl_pref = [[disc.Abreviacao for disc in disc_obrig]]
    for row in range(1, 4):
        tbl_pref.append([])
        i = tbl_pref.index([])
        for _ in range(len(tbl_pref[0])):
            tbl_pref[i].append([])

        for pref in pref_semestre:
            if pref.nivel == row:
                j = tbl_pref[0].index(pref.CoDisc.Abreviacao)
                tbl_pref[row][j].append(pref.NumProf.Apelido)

    context = {
        "rest_horarios": restricoes_profs,
        "tbl_pref": tbl_pref,
        "semestre": semestre,
        "tProfs": tbl_vls,
        "auto_profs": auto_profs,
        "detalhes_profs": detalhes_profs,
        "cods_tbl_hr": cods_tbl_hr,
        "cods_tbl_hr_ext": cods_tbl_hr_ext,
        "mtr_auto_nome": mtr_auto_nome,
        "tables_info": tables_info,
        "impedimentos_totais": impedimentos_totais,
        "tbl_extra": tbl_extra,
        "anoAberto": AnoAberto.objects.get(id=1).Ano,
        "ano": ano
    }
    return render(request, "table/index.html", context)


def atribuir_tbl_values(tbl, cod_disc, row, col, prof):
    tbl[row][
        col
    ] = f"{str(cod_disc.CoDisc)} {str(cod_disc.Abreviacao)}"
    tbl[row][col + 1] = prof

@login_required
def menu(request):
    ano = int(AnoAberto.objects.get(id=1).Ano)

    # Obtém as disciplinas obrigatórias e anota se elas têm turmas associadas ao ano específico
    disciplinas = Disciplina.objects.filter(TipoDisc="obrigatoria").annotate(
        has_turmas_no_ano=Count('turma', filter=Q(turma__Ano=ano, turma__Eextra="N"))
    ).order_by("SemestreIdeal")

    # Obtém as disciplinas que não têm turmas associadas ao ano específico
    discs_incompletas = disciplinas.exclude(has_turmas_no_ano=3)
    dict_incompletas = {}

    for disc in discs_incompletas:
        turmas = disc.turma_set.filter(Eextra="N", Ano=ano).exclude(CoDisc__CoDisc="ACH0041")
        turmas_obrig = [2, 4, 94]
        if turmas:
            for tur in turmas:
                print(tur.CodTurma)
                turmas_obrig.remove(tur.CodTurma)

        formatted_turmas = [f"{num:02d}" for num in turmas_obrig]
        result_string = ", ".join(formatted_turmas)

        dict_incompletas[disc.Abreviacao] = {

            "disc": disc,
            "faltando": result_string,
            "smt": "impar" if disc.SemestreIdeal % 2 else "par"
        }

    faltando_hrs = {}
    turmas = Turma.objects.filter(Ano=ano)
    profs = Professor.objects.all()

    for tur in turmas:
        if not tur.NroUSP.Apelido:
            continue
        nome = tur.NroUSP.Apelido
        cred = tur.CoDisc.CreditosAula

        if nome not in faltando_hrs:
            inicializa_prof(faltando_hrs, nome)

        hrs = faltando_hrs[nome][tur.SemestreAno]

        if hrs != -1:
            faltando_hrs[nome][tur.SemestreAno] += cred

        if hrs + cred >= 8:
            faltando_hrs[nome][tur.SemestreAno] = -1

    for prof in profs:
        nome = prof.Apelido
        #PRECISA CONSIDERAR PG

        pg_par = prof.PG_1_semestre
        pg_impar = prof.PG_2_semestre

        if nome not in faltando_hrs:
            inicializa_prof(faltando_hrs, nome)

    anos_ant = [i for i in range(ano - 5, ano)]
    context = {
        "anos_ant": anos_ant,
        "anoAberto": ano,
        "sem_tur": dict_incompletas,
        "falta_aula": faltando_hrs
    }
    return render(request, "table/menu.html", context)

@login_required
def redirect(request):
    if request.method == "POST":
        valor_semestre = request.POST["select1"]
        ano = request.POST["anoSelecionado"]
        diretorio = str("/table/" + valor_semestre + "/" + ano + "/")
        return HttpResponseRedirect(diretorio)
    else:
        return HttpResponse("fail")

@login_required
def save_modify(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if not is_ajax:
        return HttpResponseBadRequest('Invalid request')
    if request.method != 'POST':
        return JsonResponse({'status': 'Invalid request'}, status=400)

    data = json.load(request)
    info_par = data["info"]
    print("Aqui está o info_par")
    print(info_par)
    print("Aqui está o data")
    print(data)
    ano = AnoAberto.objects.get(id=1).Ano

    erros = {}
    alertas = {}
    ind_modif = []

    if info_par["tipo"] == "d":
        deletar_valor(data, ano, erros)

    elif info_par["tipo"] == "i":

        # caso de RP
        if info_par["cod_disc"] == "ACH0042":

            aula_manha_noite(data, alertas, ano)
            aula_noite_outro_dia_manha(data, alertas, ano)

            if not aula_msm_horario(info_par, ano, data, erros):
            
                turma_obj = cadastrar_turma_RP(info_par, ano, data["semestre"])
                update_prof(info_par, ano, data["semestre"])
                atualizar_dia(turma_obj, info_par, ano, erros, data["semestre"], ind_modif)
                
        else:

            aula_manha_noite(data, alertas, ano)
            aula_noite_outro_dia_manha(data, alertas, ano)

            if not aula_msm_horario(info_par, ano, data, erros):
            
                turma_obj = cadastrar_turma(info_par, ano, data["semestre"])
                update_prof(info_par, ano, data["semestre"])
                atualizar_dia(turma_obj, info_par, ano, erros, data["semestre"], ind_modif)

    elif info_par["tipo"] == "u":

        if "ant_prof" in info_par:
            aula_manha_noite(data, alertas, ano)
            aula_noite_outro_dia_manha(data, alertas, ano)

            if not aula_msm_horario(info_par, ano, data, erros):
                if info_par["cod_disc"] == "ACH0042":
                    deletar_valor_RP(data, ano, erros)
                    aula_manha_noite(data, alertas, ano)
                    aula_noite_outro_dia_manha(data, alertas, ano)

                    if not aula_msm_horario(info_par, ano, data, erros):
                    
                        turma_obj = cadastrar_turma_RP(info_par, ano, data["semestre"])
                        update_prof(info_par, ano, data["semestre"])
                        atualizar_dia(turma_obj, info_par, ano, erros, data["semestre"], ind_modif)
                else:
                    turma_obj = update_prof(info_par, ano, data["semestre"])
                    indice_tbl_update(turma_obj, ind_modif, info_par)

        elif "ant_cod" in info_par:
            update_cod(data, ano, erros, data["semestre"], ind_modif)

    return JsonResponse({'erros': erros, 'alertas': alertas, 'cells_modif': ind_modif})

@login_required
def download_zip_planilhas(request):
    # content-type of response
    if request.method == "POST":
        ano = request.POST["ano_xlsx"]
        # cria o arquivo zip
        z = zipfile.ZipFile('Planilhas_graduação_SI.zip', 'w', zipfile.ZIP_DEFLATED)

        # planilha de docentes
        cwd = os.getcwd()
        file_path = os.path.join(cwd, "table/static/table/docentes.xlsx")
        source_workbook = load_workbook(filename=file_path)
        sheet_doc = source_workbook["docentes"]
        planilha_docentes(sheet_doc)
        source_workbook.save("Docentes.xlsx")
        source_workbook.close()
        z.write("Docentes.xlsx")

        # planilha de distribuição semestres pares
        planilha_distribuição_semestre("par", ano)
        z.write("Distribuição_par.xlsx")

        # planilha de distribuição semestres impares
        planilha_distribuição_semestre("impar", ano)
        z.write("Distribuição_impar.xlsx")

        z.close()

        zip_arc = open("Planilhas_graduação_SI.zip", "rb")
        response = HttpResponse(zip_arc, content_type='application/x-gzip')
        response["Content-Disposition"] = 'attachment; filename="Planilhas_graduação_SI.zip"'

        # limpa os arquivos criados no processo
        os.remove("Docentes.xlsx")
        os.remove("Distribuição_impar.xlsx")
        os.remove("Distribuição_par.xlsx")
        os.remove("Planilhas_graduação_SI.zip")

        return response
    else:
        return "erro"


def planilha_distribuição_semestre(semestre, ano):
    wb = openpyxl.Workbook()
    sheet_si = wb.active
    sheet_si.title = "SI"
    planilha_si(sheet_si, semestre, ano)
    sheet_extra = wb.create_sheet("Extra")
    planilha_extra(sheet_extra, ano)
    wb.save(f"Distribuição_{semestre}.xlsx")
    wb.close()


@login_required
def pref_planilha(request):
    if request.method == "POST":
        excel_file = request.FILES.get("excel_file", None)
        excel_type = request.POST["excel_type"]

        if not excel_file:
            return render(
                request, "table/menu.html", {"error_message": "Nenhum arquivo enviado."}
            )

        if not excel_file.name.endswith(".xlsx"):
            return render(
                request,
                "table/menu.html",
                {
                    "error_message": "Formato de arquivo inválido. Por favor, envie um arquivo do tipo .xlsx."
                },
            )

        try:
            workbook = openpyxl.load_workbook(excel_file)
            worksheet = workbook.active
            profs = Professor.objects.all()
            ano = AnoAberto.objects.get(id=1).Ano

            header = [cell.value for cell in worksheet[1]]
            if excel_type == "pref_disc_hro":
                Preferencias.objects.filter(AnoProf=ano).delete()
                Restricao.objects.all().delete()
                MtvRestricao.objects.all().delete()

            for row in worksheet.iter_rows(min_row=2, max_col=39, values_only=True):

                email = row[1]
                if not isinstance(email, str) or email == "":
                    continue

                prof_encontrado = False
                email_professor = False

                # consultar direto o email
                for prof in profs:
                    if email == prof.Email:
                        email_professor = email
                        prof_encontrado = True

                if not prof_encontrado:
                    continue

                semestre_par = True if excel_type == "pref_hro_2" else False
                # executar essa linha direto, com o email da planilha usando o try catch
                prof_db = Professor.objects.get(Email=email_professor)

                if semestre_par:
                    prof_db.consideracao2 = row[9]
                else:
                    prof_db.consideracao1 = row[37]
                    prof_db.pos_doc = row[33]
                    prof_db.pref_optativas = row[32]
                    pref_disc_excel_impar("impar", row, prof_db, header)
                    pref_disc_excel_impar("par", row, prof_db, header)

                prof_db.save()
                pref_horarios(row, prof_db, semestre_par)

                # print(f"coluna AI{row[34]}, coluna AK{pref_horario}")
            return render(
                request,
                "table/menu.html",
                {"success_message": "Dados de preferência salvos com sucesso."},
            )
        except Exception as e:
            print(e)
            return render(
                request,
                "table/menu.html",
                {"error_message": "Ocorreu um erro ao processar o arquivo."},
            )

    return render(request, "table/menu.html")


def inicializa_prof(dicio, nome):
    # falta somar a pg do ano
    dicio[nome] = {
        "I": 0,
        "P": 0
    }
