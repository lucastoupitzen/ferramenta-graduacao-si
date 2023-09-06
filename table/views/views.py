import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
from openpyxl.reader.excel import load_workbook
from django.http import HttpResponseRedirect
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


    vls_turmas = Turma.objects.filter(
        Q(CoDisc__SemestreIdeal=semestre, Ano=ano) | Q(Ano=ano, Eextra="S")
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
    dict_info = {}

    #Decide quais restrição serão carregadas
    #Tem um erro de modelagem que precisa ser consertado,
    #as restrições de horário são só de primeiro semestre ou de segundo
    s_rest = "2" if semestre % 2 else "1,2"

    auto_profs = {} #para o autocomplete do nome do professor com apelido
    detalhes_profs = {}
    for prof_obj in profs_objs:
        #Já carrega dados necessários para as sugestões e detalhes do professor
        nome = unicodedata.normalize("NFD", prof_obj.NomeProf.lower())
        auto_profs[prof_obj.NomeProf] = prof_obj.Apelido
        consideracao = prof_obj.consideracao1 if semestre % 2 else prof_obj.consideracao2
        detalhes_profs[nome] = [prof_obj.NomeProf, prof_obj.Apelido, prof_obj.pos_doc, prof_obj.pref_optativas, consideracao]

        # tentar melhorar desempenho da linha abaixo
        restricoes = prof_obj.restricao_set.filter(semestre=s_rest)

        dict_info[str(prof_obj.Apelido)] = []
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

            if str(prof_obj.Apelido) in dict_info:
                dict_info[str(prof_obj.Apelido)] += list_rest_indice
            else:
                dict_info[str(prof_obj.Apelido)] = list_rest_indice

    print(dict_info)

    discs = Disciplina.objects.all()
    cods_tbl_hr = {}
    cods_tbl_hr_ext = {}  # códigos para preencher a tabela de matérias que não são do semestre selecionado
    mtr_auto_nome = {}  # auxilia no autocomplete para encontrar o código da turma extra

    for disc in discs:
        if disc.SemestreIdeal == semestre:
            cods_tbl_hr[f"{disc.CoDisc} {disc.Abreviacao}"] = disc.CoDisc
        else:
            cods_tbl_hr_ext[f"{disc.CoDisc} {disc.Abreviacao}"] = disc.CoDisc
            mtr_auto_nome[disc.NomeDisc] = f"{disc.CoDisc} {disc.Abreviacao}"


    #Serve para listar as disciplinas na página
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
        "rest_horarios": dict_info,
        "tbl_pref": tbl_pref,
        "semestre": semestre,
        "tProfs": tbl_vls,
        "auto_profs": auto_profs,
        "detalhes_profs": detalhes_profs,
        "cods_tbl_hr": cods_tbl_hr,
        "cods_tbl_hr_ext": cods_tbl_hr_ext,
        "mtr_auto_nome": mtr_auto_nome,
        "tables_info": tables_info,
    }
    return render(request, "table/index.html", context)


def menu(request):
    return render(request, "table/menu.html")


def redirect(request):
    if request.method == "POST":
        valor_semestre = request.POST["select2"]
        diretorio = str("/table/" + valor_semestre + "/")
        return HttpResponseRedirect(diretorio)
    else:
        return HttpResponse("fail")


def save_modify(request):
    if request.method == "POST":
        data = json.load(request)
        tbl_user = data.get("turmas_cadastro")
        smt = data.get("semestre")

        print(tbl_user)

        ano = datetime.now().year
        dias = Dia.objects.all()

        deletar_valores(dias, tbl_user, ano, smt)

        tbl_user, tbl_user_invalidos, razao_extrapolo = limite_registro_profs(tbl_user)

        conflitos = ""
        for turma in tbl_user_invalidos:
            tem_conflito = conflito_hro(turma, ano, smt)
            if tem_conflito:
                conflitos += f"{tem_conflito}"

        for turma in tbl_user:
            turma_db = Turma.objects.filter(
                Q(
                    CoDisc=turma["cod_disc"],
                    CodTurma=turma["cod_turma"],
                    Ano=ano,
                    CoDisc__SemestreIdeal=smt,
                    Eextra="N",
                )
                | Q(
                    CoDisc=turma["cod_disc"],
                    CodTurma=turma["cod_turma"],
                    Ano=ano,
                    Eextra="S",
                )
            )
            if not turma_db.exists():
                cadastrar_turma(turma, ano, smt)

            dia = Dia.objects.filter(Horario=turma["horario"], DiaSemana=turma["dia"])

            if not dia.exists():
                cadastrar_dia(turma, ano, smt)
            else:
                dia = Dia.objects.get(
                    Horario=turma["horario"], DiaSemana=turma["dia"]
                )  # melhorar isso
                existe_dia_turma = False
                t_relacionadas_dia = dia.Turmas.all()

                for t_dia in t_relacionadas_dia:
                    existe_dia_turma = existe_turma_user(t_dia, turma, ano)

                if not existe_dia_turma:
                    tem_conflito = atualizar_dia(turma, dia, ano, smt)
                    if tem_conflito:
                        conflitos += f"{tem_conflito}"

        response_data = {
            "conflitos_prof_semestres": conflitos,
            "prof_turma_extrapolando": razao_extrapolo,
        }
        return JsonResponse(response_data)

    return HttpResponse("fail")


#Nova implementaçao para salvar automaticamente as
#alterações no quando cada par de célula é editada.
##


def atualizar_dia(turma, dia, ano, smt):
    turma_bd = Turma.objects.get(
        CoDisc=turma["cod_disc"], CodTurma=turma["cod_turma"], Ano=ano
    )
    conflito = conflito_hro(turma, ano, smt)
    if conflito:
        return conflito
    else:
        dia.Turmas.add(turma_bd)


def download_excel_data(request):
    # content-type of response
    if request.method == "POST":
        select_worksheet = request.POST.get("type")
        semestre_tbl = request.POST.get("semestre")
        response = HttpResponse(content_type="application/ms-excel")
        # decide file name
        response["Content-Disposition"] = 'attachment; filename="PlanilhaSI.xlsx"'

        if select_worksheet == "docente":
            cwd = os.getcwd()
            file_path = os.path.join(cwd, "table/static/table/docentes.xlsx")
            source_workbook = load_workbook(filename=file_path)
            sheet_doc = source_workbook["docentes"]
            planilha_docentes(sheet_doc)
            source_workbook.save(response)
            source_workbook.close()

        else:
            wb = openpyxl.Workbook()
            sheet_si = wb.active
            sheet_si.title = "SI"
            planilha_si(sheet_si, semestre_tbl)
            sheet_extra = wb.create_sheet("Extra")
            planilha_extra(sheet_extra)
            wb.save(response)
            wb.close()

        return response
    else:
        return "erro"


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

                for prof in profs:
                    if email == prof.Email:
                        email_professor = email
                        prof_encontrado = True

                if not prof_encontrado:
                    continue

                semestre_par = True if excel_type == "pref_hro_2" else False
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
