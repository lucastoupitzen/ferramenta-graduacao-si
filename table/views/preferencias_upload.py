from datetime import datetime
from table.models import *
import re
import unidecode


def pref_disc_excel_impar(sem, row, prof_db, header):
    values = (
        # [row for row in row[2:18]] if sem == "impar" else [row for row in row[18:32]] antiga
        [row for row in row[2:16]] if sem == "impar" else [row for row in row[16:30]]
    )
    ano = AnoAberto.objects.get(id=1).Ano
    ini = 18 if sem == "par" else 2
    for i, value in enumerate(values, start=ini):
        if value is None or value == "Não Selecionado":
            continue
        col_value = header[i]
        cod_mtr = re.search(r"ACH\d{4}", col_value)
        semestre = 2 if sem == "par" else 1

        disc_bd = Disciplina.objects.get(CoDisc=cod_mtr.group())
        preferencia = Preferencias(
            NumProf=prof_db,
            CoDisc=disc_bd,
            AnoProf=ano,
            nivel=int(value),
            Semestre=semestre,
        )
        preferencia.save()



def pref_horarios(row, prof_db, semestre_par):
    if semestre_par:
        MtvRestricao.objects.filter(restricao__semestre="2", restricao__nro_usp=prof_db).delete()
        Restricao.objects.filter(semestre="2", nro_usp=prof_db).delete()
        values = [row for row in row[3:7]]
        dias_semana = ["segunda", "terca", "quarta", "quinta", "sexta"]

        mtv_prof = None
        if row[8] is not None:
            mtv_prof = MtvRestricao(mtv=row[8])
            mtv_prof.save()

        for dia, value in zip(dias_semana, values):
            if value is not None:
                per = unidecode.unidecode(value.lower())
                restHro = Restricao(periodo=per, dia=dia, nro_usp=prof_db, semestre="2")
                if mtv_prof:
                    restHro.motivos = mtv_prof
                restHro.save()

    if semestre_par and row[2] is not None:
        dia = unidecode.unidecode(row[2].lower())
        Restricao.criar_restricoes(
            periodo="todos_periodos", dia=dia, nro_usp=prof_db, semestre="2"
        )
    if semestre_par and row[36] is not None:
        dia = unidecode.unidecode(row[36].lower())
        # print(f"dia {dia} professor: {prof_db.NomeProf}")
        Restricao.criar_restricoes(
            periodo="todos_periodos", dia=dia, nro_usp=prof_db, semestre="1"
        )

    # if not semestre_par and row[34] is not None: versão antiga
    # 37, 38, 39


    manha = row[37]
    tarde = row[38]
    noite = row[39]

    variaveis = {
        manha: "manha",
        tarde: "tarde",
        noite: "noite"
    }

    if not semestre_par:

        for dia in (manha, tarde, noite):
            if dia is None:
                continue

            # dia, per = row[34].split()

            dia = unidecode.unidecode(dia.lower())
            Restricao.criar_restricoes(
                    periodo=variaveis[dia], dia=dia, nro_usp=prof_db, semestre="1", impedimento=True
                )
            # print(f"dia: {dia} periodo: {per} professor: {prof_db.NomeProf}")
            rest = prof_db.restricao_set.filter(
                dia=dia, periodo=variaveis[dia], semestre="1"
            ).first()

            mtv_prof = False

            if row[35] is not None:
                mtv_prof = MtvRestricao(mtv=row[35])
                mtv_prof.save()

            if not rest:
                rest = Restricao(periodo=per, dia=dia, nro_usp=prof_db, semestre="1")

            if rest and mtv_prof:
                rest.motivos = mtv_prof

            rest.save()

    if row[36] is not None:
        dia = unidecode.unidecode(row[36].lower())
        # print(f"dia {dia} professor: {prof_db.NomeProf}")
        Restricao.criar_restricoes(
            periodo="todos_periodos", dia=dia, nro_usp=prof_db, semestre="1"
        )