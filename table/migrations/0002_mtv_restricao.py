# Generated by Django 4.1.6 on 2023-05-14 03:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("table", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mtv_restricao",
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
                ("mtv", models.CharField(default="", max_length=225)),
            ],
        ),
    ]
