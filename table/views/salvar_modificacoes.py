from table.models import *
from django.db.models import Q


def update_prof(inf, year):
    turma_db = Turma.objects.get(Ano=year, CoDisc=str(inf["cod_disc"]),  CodTurma=str(inf["cod_turma"]))
    prof = Professor.objects.get(Apelido=inf["professor"])
    turma_db.NroUSP = prof
    turma_db.save()


def update_cod(inf, year, erros):
    turma_obj = cadastrar_turma(inf, year)
    atualizar_dia(turma_obj, inf, year, erros)


def deletar_valor(infos_user, year, erros):
    # Iterar sobre as turmas do banco de dados e excluir aquelas que não estão em tbl_user
    try:
        dia = Dia.objects.get(DiaSemana=int(infos_user["dia"]), Horario=int(infos_user["horario"]))
        obj_turma  = dia.Turmas.get(Ano=year, CoDisc=str(infos_user["cod_disc"]), \
                                    CodTurma=str(infos_user["cod_turma"]))
        num_days_turma = obj_turma.dia_set.all()
        
        if(len(num_days_turma) > 1):
            obj_turma.dia_set.remove(dia)
        else:
            obj_turma.delete()

    except:
        erros["delecao"] = "Erro ao deletar par de células\n"


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


def atualizar_dia(turma_db, turma, year, erros):
    if not turma_db:
        turma_db = Turma.objects.get(Ano=year, CoDisc=str(turma["cod_disc"]), \
                                     CodTurma=str(turma["cod_turma"]))
    
    dia = Dia.objects.filter(DiaSemana=int(turma["dia"]), Horario=int(turma["horario"]))
    
    if extrapola_creditos(turma_db):
        erros["credito"] = f"Matéria {turma['cod_disc']} e código de turma {turma['cod_turma']} extrapola o número de créditos-aula\n"
        return False
    
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
   

#Essa implementação não leva em conta turma extra
# precisará adicionada a parte que considera 
# quando o sistema permitir turma extra noite e manhã 
def aula_manha_noite(data, alertas):
    inf = data["info"]
    # lista das linhas que representam a manhã e noite
    if inf["horario"] not in [0,1,5,7]: return False
    
    horario = (0,1) if inf["horario"] in [5,7] else (5,7)
    
    manha_noite = Dia.objects.filter(DiaSemana=inf["dia"], Horario__in=horario,\
                             Turmas__NroUSP__Apelido=inf["professor"], \
                              Turmas__CoDisc__SemestreIdeal=data["semestre"])
    if manha_noite:
        dia = manha_noite.first().get_DiaSemana_display().lower()
        alertas["aula_manha_noite"] = (f"Professor(a) {inf['professor']} vai "
                                       f"estar dando aula de manhã e a noite na {dia}.\n")
    

#a mesma observação da função imediatamente acima vale para essa
def aula_noite_outro_dia_manha(data, alertas):
    inf = data["info"]
    
    # o horário precisa ser do matutino 1 e diferente de segunda-feira
    # OU do noturno 2 e diferente de sexta-feira
    if (inf["horario"] != 7 and inf["dia"] == 8) or \
        (inf["horario"] != 0 and inf["dia"] == 0): 
        #Tem um valor que deve ser aceito
        #que é segunda noturno 2
        if not (inf["horario"] == 7 and inf["dia"] == 0):
            return False
    
    
    # Um dicionário para evitar mais uma consulta
    dias = {0: "segunda", 2: "terça", 4: "quarta", 6: "quinta", 8: "sexta"}

    ind_lado_dia = int(inf["dia"]) + 2 if inf["horario"] == 7 else int(inf["dia"]) - 2
    hr = 0 if inf["horario"] == 7 else 7
    
    dia_alerta = Dia.objects.filter(DiaSemana=ind_lado_dia, Horario=hr,\
                             Turmas__NroUSP__Apelido=inf["professor"], \
                              Turmas__CoDisc__SemestreIdeal=data["semestre"])
    
    if dia_alerta:
        dia = dia_alerta.first().get_DiaSemana_display().lower()
        dia_lado = dias[inf['dia']]
        
        if inf["horario"] == 0:
            aux = dia
            dia = dia_lado
            dia_lado = aux

        alertas["alert2"] = (f"Professor(a) {inf['professor']} vai estar dando "
                          f"aula na noite de {dia_lado} e de manhã na {dia}\n")
    

def aula_msm_horario(inf, ano, data, erros):
    smt = data["semestre"]
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
        msg = (
            f"Conflito na {str(conflito_hr.first())}"
            f" do professor(a) {inf['professor']}"
            f" com o semestre {aux.CoDisc.SemestreIdeal}\n"
        )
        erros["prof_msm_hr"] = msg
        return True



