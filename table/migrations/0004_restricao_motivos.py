# Generated by Django 4.1.6 on 2023-05-14 03:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("table", "0003_rename_mtv_restricao_mtvrestricao"),
    ]

    operations = [
        migrations.AddField(
            model_name="restricao",
            name="motivos",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="table.mtvrestricao",
            ),
        ),
    ]
