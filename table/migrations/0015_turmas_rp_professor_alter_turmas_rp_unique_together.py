# Generated by Django 4.1.6 on 2023-10-20 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("table", "0014_turmas_rp"),
    ]

    operations = [
        migrations.AddField(
            model_name="turmas_rp",
            name="professor",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="table.professor",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="turmas_rp",
            unique_together={("turma", "professor")},
        ),
    ]