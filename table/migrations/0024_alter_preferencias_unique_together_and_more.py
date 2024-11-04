# Generated by Django 4.1.6 on 2024-05-04 19:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("table", "0023_taditurma_diaaulatadi"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="preferencias",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="diaaulatadi",
            name="horario",
            field=models.CharField(
                choices=[
                    ("8:00 - 09:45h", "8:00 - 09:45h"),
                    ("10:15 - 12:00h", "10:15 - 12:00h"),
                    ("14:00 - 15:45h", "14:00 - 15:45h"),
                    ("16:15 - 18:00h", "16:15 - 18:00h"),
                    ("19:00 - 20:45h", "19:00 - 20:45h"),
                    ("21:00 - 22:45h", "21:00 - 22:45h"),
                ],
                default=None,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="preferencias",
            name="AnoProf",
            field=models.DecimalField(decimal_places=0, default=2024, max_digits=4),
        ),
        migrations.AlterUniqueTogether(
            name="preferencias",
            unique_together={("NumProf", "CoDisc", "AnoProf")},
        ),
    ]