# Generated by Django 4.1.6 on 2023-11-12 17:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("table", "0015_turmas_rp_professor_alter_turmas_rp_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnoAberto",
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
                    "Ano",
                    models.DecimalField(decimal_places=0, default=2022, max_digits=4),
                ),
            ],
        ),
    ]
