from table.models import *
from django.db.models import Q


def update_prof(inf, year, smt):
    smt_ano = "I" if smt % 2 else "P"
    extra = "N"
    if inf["extra"]:
        extra = "S"

    turma_db = Turma.objects.get(Ano=year, CoDisc=str(inf["cod_disc"]),
                                 CodTurma=str(inf["cod_turma"]), SemestreAno=smt_ano, Eextra=extra)
    prof = Professor.objects.get(Apelido=inf["professor"])
    turma_db.NroUSP = prof
    turma_db.save()
    return turma_db


def update_prof_RP(inf, year, smt):
    smt_ano = "I" if smt % 2 else "P"
    extra = "N"
    if inf["extra"]:
        extra = "S"

    turma_db = Turma.objects.get(Ano=year, CoDisc=str(inf["cod_disc"]),
                                 CodTurma=str(inf["cod_turma"]), SemestreAno=smt_ano, Eextra=extra)
    prof = Professor.objects.get(Apelido=inf["professor"])
    turma_db.NroUSP = prof
    turma_db.save()
    prof_RP = Professor.objects.get(Apelido=inf["ant_prof"])
    turma_RP = Turmas_RP.objects.get(turma=turma_db, professor=prof_RP)
    turma_RP.professor = prof
    turma_RP.save()
    return turma_db


def update_cod(data, year, erros, smt, ind_modif):
    inf = data["info"]
    deletar_valor(data, year, erros)
    turma_obj = cadastrar_turma(inf, year, smt)
    update_prof(inf, year, data["semestre"])
    atualizar_dia(turma_obj, inf, year, erros, smt, ind_modif)


def deletar_valor(data, year, erros):
    # Iterar sobre as turmas do banco de dados e excluir aquelas que não estão em tbl_user
    infos_user = data["info"]
    smt_ano = "I" if data["semestre"] % 2 else "P"

    codisc = ""
    if infos_user["tipo"] == "u":
        codisc = infos_user["ant_cod"].split()[0]
    else:
        codisc = infos_user["cod_disc"]

    try:
        dia = Dia.objects.get(DiaSemana=int(infos_user["dia"]), Horario=int(infos_user["horario"]))
        obj_turma = dia.Turmas.get(Ano=year, CoDisc=codisc,
                                   CodTurma=str(infos_user["cod_turma"]), SemestreAno=smt_ano)
        num_days_turma = obj_turma.dia_set.all()
        
        if len(num_days_turma) > 1:
            obj_turma.dia_set.remove(dia)
        else:
            obj_turma.delete()

    except:
        erros["delecao"] = "Erro ao deletar par de células\n"


def deletar_valor_RP(data, year, erros):
    # Iterar sobre as turmas do banco de dados e excluir aquelas que não estão em tbl_user
    infos_user = data["info"]
    smt_ano = "I" if data["semestre"] % 2 else "P"

    codisc = "ACH0042"

    try:
        dia = Dia.objects.get(DiaSemana=int(infos_user["dia"]), Horario=int(infos_user["horario"]))
        obj_turma = dia.Turmas.get(Ano=year, CoDisc=codisc,
                                   CodTurma=str(infos_user["cod_turma"]), SemestreAno=smt_ano)
        num_days_turma = obj_turma.dia_set.all()
        
        if len(num_days_turma) > 1:
            obj_turma.dia_set.remove(dia)
        else:
            obj_turma.delete()

    except:
        return


def cadastrar_turma_RP(turma, ano, smt):

    extra = "N"
    if turma["horario"] in (2, 4) or turma["extra"]:
        extra = "S"

    smt_ano = "I" if smt % 2 else "P"

    try:
        nova_turma = Turma.objects.create(
            CoDisc=Disciplina.objects.get(CoDisc=turma["cod_disc"]),
            CodTurma=turma["cod_turma"],
            Ano=ano,
            NroUSP=Professor.objects.get(Apelido=turma["professor"]),
            Eextra=extra,
            SemestreAno=smt_ano
        )
        nova_turma.save()
        nova_turma_RP = Turmas_RP(
        turma = nova_turma,
        professor = Professor.objects.get(Apelido=turma["professor"]),
        )
        try:
            nova_turma_RP.save()
        except:
            print("erro")
            return False
    except:
        nova_turma = Turma.objects.get(
        CoDisc=Disciplina.objects.get(CoDisc=turma["cod_disc"]),
        CodTurma=turma["cod_turma"],
        Ano=ano,
        Eextra=extra,
        SemestreAno=smt_ano
        )
        nova_turma_RP = Turmas_RP(
        turma = nova_turma,
        professor = Professor.objects.get(Apelido=turma["professor"]),
        )
        try:
            nova_turma_RP.save()
        except:
            return False
    
    return nova_turma


def cadastrar_turma(turma, ano, smt):
    extra = "N"
    if turma["horario"] in (2, 4) or turma["extra"]:
        extra = "S"

    smt_ano = "I" if smt % 2 else "P"

    nova_turma = Turma.objects.create(
        CoDisc=Disciplina.objects.get(CoDisc=turma["cod_disc"]),
        CodTurma=turma["cod_turma"],
        Ano=ano,
        NroUSP=Professor.objects.get(Apelido=turma["professor"]),
        Eextra=extra,
        SemestreAno=smt_ano
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


def atualizar_dia(turma_db, turma, year, erros, smt, ind_modif):
    smt_ano = "I" if smt % 2 else "P"

    extra = "N"
    if turma["extra"]:
        extra = "S"

    if not turma_db:
        turma_db = Turma.objects.get(Ano=year, CoDisc=str(turma["cod_disc"]),
                                     CodTurma=str(turma["cod_turma"]), SemestreAno=smt_ano, Eextra=extra)
    
    dia = Dia.objects.filter(DiaSemana=int(turma["dia"]), Horario=int(turma["horario"]))

    indice_tbl_update(turma_db, ind_modif, turma)

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
    
    horario = (0, 1) if inf["horario"] in [5,7] else (5,7)

    if data["semestre"] % 2 == 0:
            semestres_testados = [2,4,6,8]
    else:
            semestres_testados = [1,3,5,7]
        
    for semestre in semestres_testados:

            manha_noite = Dia.objects.filter(DiaSemana=inf["dia"], Horario__in=horario,
                                                Turmas__NroUSP__Apelido=inf["professor"],
                                                Turmas__CoDisc__SemestreIdeal=semestre)
            
            if manha_noite: break


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

    if data["semestre"] % 2 == 0:
        semestres_testados = [2,4,6,8]
    else:
        semestres_testados = [1,3,5,7]
    
    for semestre in semestres_testados:
        dia_alerta = Dia.objects.filter(DiaSemana=ind_lado_dia, Horario=hr,
                                    Turmas__NroUSP__Apelido=inf["professor"],
                                    Turmas__CoDisc__SemestreIdeal=semestre)
        if dia_alerta: break
    
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


def indice_tbl_update(turma_obj, ind_modif, info_par):
    dias_turma = turma_obj.dia_set.exclude(DiaSemana=info_par["dia"],
                                           Horario=info_par["horario"])
    for dia in dias_turma:
        row = dia.Horario
        n_row = row
        if row in (0, 1):
            n_row += 1

        if info_par["extra"]:
            if row == 5:
                n_row = 4
            elif row == 7:
                n_row = 5
        else:
            if row == 2:
                n_row = 4
            elif row == 4:
                n_row = 6
            elif row == 5:
                n_row = 8 if turma_obj.CodTurma == 4 else 9
            elif row == 7:
                n_row = 10 if turma_obj.CodTurma == 4 else 11

        ind_modif.append({
            "row": n_row,
            "col": int(dia.DiaSemana),
            "new_value": turma_obj.NroUSP.Apelido
        })
