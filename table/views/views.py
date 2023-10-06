import os
import zipfile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
from openpyxl.reader.excel import load_workbook
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import unicodedata


from .planilha_distribuicao import *
from .planilha_docentes import *
from .salvar_modificacoes import *
from .preferencias_upload import *


def index(request, semestre="2"):
    # cria listas com referências diferentes
    # elas serão iteradas no index.html para carregar os dados na planilha editável
    tbl_vls = [[""] * 11 for _ in range(8)]
    tbl_vls.insert(3, ["", ""])
    ano = datetime.now().year

    query_smt = [7, 8] if semestre in [7, 8] else [semestre]
    smt_ano = "I" if semestre % 2 else "P"
    vls_turmas = Turma.objects.filter(
        Q(CoDisc__SemestreIdeal__in=query_smt, Ano=ano, SemestreAno=smt_ano) |
        Q(Ano=ano, Eextra="S", SemestreAno=smt_ano)
    )
    for tur_materia in vls_turmas:
        cod_disc = tur_materia.CoDisc
        prof = tur_materia.NroUSP.Apelido
        t_nro = int(tur_materia.CodTurma)

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

            tbl_vls[row_tbl][
                col_tbl
            ] = f"{str(cod_disc.CoDisc)} {str(cod_disc.Abreviacao)}"
            tbl_vls[row_tbl][col_tbl + 1] = prof

            if tur_materia.Eextra == "N":
                tbl_vls[row_tbl][10] = t_nro

    # Usando os números de turma predefinidos caso esteja vazio(otimizar)
    # Isso vai funcionar somente para SI
    for row, vls in enumerate(tbl_vls):
        if row in (2, 4, 3):
            continue

        cell_turma = vls[10]
        if cell_turma != "":
            continue

        if row in (0, 1):
            tbl_vls[row][10] = 2
        elif row in (5, 7):
            tbl_vls[row][10] = 4
        else:
            tbl_vls[row][10] = 94

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
                list_rest_indice = [indice, 23, 34, 35, 36, 37]
            elif rest_prof.periodo == "tarde":
                list_rest_indice = [indice, indice + 1, indice + 14, indice + 15]
            elif rest_prof.periodo == "noite":
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
    }
    return render(request, "table/index.html", context)


def menu(request):
    return render(request, "table/menu.html")


def redirect(request):
    if request.method == "POST":
        valor_semestre = request.POST["select1"]
        diretorio = str("/table/" + valor_semestre + "/")
        return HttpResponseRedirect(diretorio)
    else:
        return HttpResponse("fail")


def save_modify(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if not is_ajax:
        return HttpResponseBadRequest('Invalid request')
    if request.method != 'POST':
        return JsonResponse({'status': 'Invalid request'}, status=400)

    data = json.load(request)
    info_par = data["info"]
    ano = datetime.now().year

    erros = {}
    alertas = {}
    ind_modif = []

    if info_par["tipo"] == "d":
        deletar_valor(data, ano, erros)

    elif info_par["tipo"] == "i":

        aula_manha_noite(data, alertas)
        aula_noite_outro_dia_manha(data, alertas)

        if not aula_msm_horario(info_par, ano, data, erros):
            turma_obj = cadastrar_turma(info_par, ano, data["semestre"])
            update_prof(info_par, ano, data["semestre"])
            atualizar_dia(turma_obj, info_par, ano, erros, data["semestre"], ind_modif)

    elif info_par["tipo"] == "u":

        if "ant_prof" in info_par:
            aula_manha_noite(data, alertas)
            aula_noite_outro_dia_manha(data, alertas)

            if not aula_msm_horario(info_par, ano, data, erros):
                turma_obj = update_prof(info_par, ano, data["semestre"])
                indice_tbl_update(turma_obj, ind_modif, info_par)

        elif "ant_cod" in info_par:
            update_cod(data, ano, erros, data["semestre"], ind_modif)

    return JsonResponse({'erros': erros, 'alertas': alertas, 'cells_modif': ind_modif})


def download_zip_planilhas(request):
    # content-type of response
    if request.method == "POST":

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
        planilha_distribuição_semestre("par")
        z.write("Distribuição_par.xlsx")

        # planilha de distribuição semestres impares
        planilha_distribuição_semestre("impar")
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


def planilha_distribuição_semestre(semestre):
    wb = openpyxl.Workbook()
    sheet_si = wb.active
    sheet_si.title = "SI"
    planilha_si(sheet_si, semestre)
    sheet_extra = wb.create_sheet("Extra")
    planilha_extra(sheet_extra)
    wb.save(f"Distribuição_{semestre}.xlsx")
    wb.close()


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

            header = [cell.value for cell in worksheet[1]]
            if excel_type == "pref_disc_hro":
                Preferencias.objects.all().delete()
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
