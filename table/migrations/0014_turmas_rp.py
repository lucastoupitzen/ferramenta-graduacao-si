# Generated by Django 4.1.6 on 2023-10-17 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("table", "0013_alter_turma_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="Turmas_RP",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "turma",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="table.turma"
                    ),
                ),
            ],
        ),
    ]
