# Generated by Django 4.1.6 on 2024-02-28 02:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("table", "0020_turma_semestre_extra"),
    ]

    operations = [
        migrations.AddField(
            model_name="disciplina",
            name="ativa",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="professor",
            name="em_atividade",
            field=models.BooleanField(default=True),
        ),
    ]
