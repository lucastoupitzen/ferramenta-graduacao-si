from table.models import *
from django.db.models import Q
import textwrap

def update_prof(inf, year):
    turma_db = Turma.objects.get(Ano=year, CoDisc=str(inf["cod_disc"]),  CodTurma=str(inf["cod_turma"]))
    prof = Professor.objects.get(Apelido=inf["professor"])
    turma_db.NroUSP = prof
    turma_db.save()


def update_cod(inf, year):
    #o update de código pode levar a inserção de turma
    turma_obj = cadastrar_turma(inf, year)
    atualizar_dia(turma_obj, inf, year)


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



# def limite_registro_profs(lista):
#     contagem = {}
#     dicio_validos = []
#     infringem_limite = []
#     lista_itens = {}
#     avisos = ""

#     for item in lista:
#         chave = (item["cod_disc"], item["cod_turma"])
#         contagem[chave] = contagem.get(chave, 0) + 1
#         lista_itens.setdefault(chave, []).append(item)

#     for chave, ocorrencias in contagem.items():
#         cod_disc, cod_turma = chave

#         creditos = Disciplina.objects.get(CoDisc=cod_disc).CreditosAula

#         if creditos == 4 and ocorrencias <= 2:
#             dicio_validos.extend(lista_itens[chave])
#         elif creditos == 2 and ocorrencias <= 1:
#             dicio_validos.extend(lista_itens[chave])
#         else:
#             infringem_limite.extend(lista_itens[chave])
#             aviso = f"==> Disciplina {cod_disc}, Turma {cod_turma}"
#             avisos += f"{aviso}"

#     return dicio_validos, infringem_limite, avisos


# def conflito_hro(turma, ano, smt):
#     prof = Professor.objects.get(Apelido=turma["professor"])
#     semestre_geral = [1, 3, 5, 7] if smt % 2 else [2, 4, 6, 8]
#     turma_prof = Turma.objects.filter(
#         NroUSP=prof, Ano=ano, CoDisc__SemestreIdeal__in=semestre_geral
#     )
#     conflito_hr = False
#     aux = False
#     for t in turma_prof:
#         if t.CoDisc.SemestreIdeal == smt:
#             continue

#         conflito_hr = t.dia_set.filter(DiaSemana=turma["dia"], Horario=turma["horario"])
#         if conflito_hr:
#             aux = t
#             break

#     if conflito_hr:
#         notif = textwrap.dedent(
#             """
#             ==> Conflito: {c}
#             ==> Professor: {prof}  
#             ==> Semestre conflitante: {smt}
#         ---------------------------""".format(
#                 c=str(conflito_hr[0]),
#                 prof=turma["professor"],
#                 smt=aux.CoDisc.SemestreIdeal,
#             )
#         )
#         return notif


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
    if dia.exists():
        dia.first().Turmas.add(turma_db)
    else:
        cadastrar_dia(turma_db, turma)
