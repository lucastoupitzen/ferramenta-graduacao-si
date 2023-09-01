from table.models import *
from django.db.models import Q
import textwrap


def deletar_valores(dias, tbl_user, year, smt):
    # Criar um conjunto com as chaves relevantes das turmas presentes em tbl_user
    tbl_user_turmas = set(
        (
            user_data["cod_disc"],
            user_data["professor"],
            int(user_data["horario"]),
            int(user_data["dia"]),
            user_data["cod_turma"],
        )
        for user_data in tbl_user
    )

    # Iterar sobre as turmas do banco de dados e excluir aquelas que não estão em tbl_user
    for dia in dias:
        turmas = dia.Turmas.filter(
            Q(Ano=year, CoDisc__SemestreIdeal=smt) | Q(Ano=year, Eextra="S")
        ).select_related("NroUSP")
        for turma in turmas:
            turma_key = (
                str(turma.CoDisc),
                turma.NroUSP.Apelido,
                dia.Horario,
                int(dia.DiaSemana),
                str(turma.CodTurma),
            )
            if turma_key not in tbl_user_turmas:
                turma.delete()


def limite_registro_profs(lista):
    contagem = {}
    dicio_validos = []
    infringem_limite = []
    lista_itens = {}
    avisos = ""

    for item in lista:
        chave = (item["cod_disc"], item["cod_turma"])
        contagem[chave] = contagem.get(chave, 0) + 1
        lista_itens.setdefault(chave, []).append(item)

    for chave, ocorrencias in contagem.items():
        cod_disc, cod_turma = chave

        creditos = Disciplina.objects.get(CoDisc=cod_disc).CreditosAula

        if creditos == 4 and ocorrencias <= 2:
            dicio_validos.extend(lista_itens[chave])
        elif creditos == 2 and ocorrencias <= 1:
            dicio_validos.extend(lista_itens[chave])
        else:
            infringem_limite.extend(lista_itens[chave])
            aviso = f"==> Disciplina {cod_disc}, Turma {cod_turma}"
            avisos += f"{aviso}"

    return dicio_validos, infringem_limite, avisos


def conflito_hro(turma, ano, smt):
    prof = Professor.objects.get(Apelido=turma["professor"])
    semestre_geral = [1, 3, 5, 7] if smt % 2 else [2, 4, 6, 8]
    turma_prof = Turma.objects.filter(
        NroUSP=prof, Ano=ano, CoDisc__SemestreIdeal__in=semestre_geral
    )
    conflito_hr = False
    aux = False
    for t in turma_prof:
        if t.CoDisc.SemestreIdeal == smt:
            continue

        conflito_hr = t.dia_set.filter(DiaSemana=turma["dia"], Horario=turma["horario"])
        if conflito_hr:
            aux = t
            break

    if conflito_hr:
        notif = textwrap.dedent(
            """
            ==> Conflito: {c}
            ==> Professor: {prof}  
            ==> Semestre conflitante: {smt}
        ---------------------------""".format(
                c=str(conflito_hr[0]),
                prof=turma["professor"],
                smt=aux.CoDisc.SemestreIdeal,
            )
        )
        return notif


def cadastrar_turma(turma, ano, smt):
    extra = "N"
    if turma["horario"] in (2, 4):
        extra = "S"
    # conflito_hro(turma, ano, smt)
    nova_turma = Turma(
        CoDisc=Disciplina.objects.get(CoDisc=turma["cod_disc"]),
        CodTurma=turma["cod_turma"],
        Ano=ano,
        NroUSP=Professor.objects.get(Apelido=turma["professor"]),
        Eextra=extra,
    )
    nova_turma.save()


def cadastrar_dia(turma_user, ano, smt):
    turma_db = Turma.objects.get(
        CoDisc=turma_user["cod_disc"], CodTurma=turma_user["cod_turma"], Ano=ano
    )
    dia_materia = Dia(DiaSemana=turma_user["dia"], Horario=turma_user["horario"])
    dia_materia.save()
    # conflito_hro(turma_user, ano, smt)
    dia_materia.Turmas.add(turma_db)


def existe_turma_user(turma_db, turma_user, year):
    cod_disc = str(turma_db.CoDisc)
    cod_turma = int(turma_db.CodTurma)
    ano_bd = turma_db.Ano

    if (
        turma_user["cod_disc"] == cod_disc
        and int(turma_user["cod_turma"]) == cod_turma
        and ano_bd == year
    ):
        return True