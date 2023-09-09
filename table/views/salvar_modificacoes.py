from table.models import *
from django.db.models import Q


def update_prof(inf, year):
    turma_db = Turma.objects.get(Ano=year, CoDisc=str(inf["cod_disc"]),  CodTurma=str(inf["cod_turma"]))
    prof = Professor.objects.get(Apelido=inf["professor"])
    turma_db.NroUSP = prof
    turma_db.save()


def update_cod(inf, year):
    turma_obj = cadastrar_turma(inf, year)
    return atualizar_dia(turma_obj, inf, year)


def deletar_valor(infos_user, year):
    # Iterar sobre as turmas do banco de dados e excluir aquelas que não estão em tbl_user
    try:
        dia = Dia.objects.get(DiaSemana=int(infos_user["dia"]), Horario=int(infos_user["horario"]))
        obj_turma  = dia.Turmas.get(Ano=year, CoDisc=str(infos_user["cod_disc"]),  CodTurma=str(infos_user["cod_turma"]))
        num_days_turma = obj_turma.dia_set.all()
        
        if(len(num_days_turma) > 1):
            obj_turma.dia_set.remove(dia)
        else:
            obj_turma.delete()
    except:
        return "Erro ao deletar par de células"


def cadastrar_turma(turma, ano):
    extra = "N"
    if turma["horario"] in (2, 4):
        extra = "S"

    nova_turma = Turma(
        CoDisc=Disciplina.objects.get(CoDisc=turma["cod_disc"]),
        CodTurma=turma["cod_turma"],
        Ano=ano,
        NroUSP=Professor.objects.get(Apelido=turma["professor"]),
        Eextra=extra,
    )
    try:
        nova_turma.save()
        return nova_turma
    except:
        return False
    

def cadastrar_dia(turma_db, turma_user):
    dia_materia = Dia(DiaSemana=turma_user["dia"], Horario=turma_user["horario"])
    dia_materia.save()
    dia_materia.Turmas.add(turma_db)


def atualizar_dia(turma_db, turma, year):
    if not turma_db:
        turma_db = Turma.objects.get(Ano=year, CoDisc=str(turma["cod_disc"]),  CodTurma=str(turma["cod_turma"]))
    
    dia = Dia.objects.filter(DiaSemana=int(turma["dia"]), Horario=int(turma["horario"]))
    
    if extrapola_creditos(turma_db):
        return f"Matéria {turma['cod_disc']} e código de turma {turma['cod_turma']} extrapola o número de créditos-aula"
    
    if dia.exists():
        dia.first().Turmas.add(turma_db)
    else:
        cadastrar_dia(turma_db, turma)


def extrapola_creditos(turma_db):
    creditos_disc = turma_db.CoDisc.CreditosAula
    num_hrs = turma_db.dia_set.all().count()
   
    if (creditos_disc == 4 and num_hrs == 2) or \
    (creditos_disc == 2 and num_hrs == 1):
        return True
   


def aula_msm_horario(inf, ano, smt):
    prof = Professor.objects.get(Apelido=inf["professor"])
    semestre_geral = [1, 3, 5, 7] if smt % 2 else [2, 4, 6, 8]
    turma_prof = Turma.objects.filter(
        NroUSP=prof, Ano=ano, CoDisc__SemestreIdeal__in=semestre_geral
    )
    conflito_hr = False
    aux = False
    for t in turma_prof:
        if t.CoDisc.SemestreIdeal == smt:
            continue

        conflito_hr = t.dia_set.filter(DiaSemana=inf["dia"], Horario=inf["horario"])
        if conflito_hr:
            aux = t
            break

    if conflito_hr:
        msg = {
            "conflito": str(conflito_hr.first()),
            "professor": inf["professor"],
            "smt_conflitante": aux.CoDisc.SemestreIdeal
        }
        return msg


