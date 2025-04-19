# Generated by Django 4.2.20 on 2025-04-19 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_alter_exchangeproposal_unique_together_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="exchangeproposal",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="exchangeproposal",
            name="status",
            field=models.CharField(
                choices=[
                    ("ожидает", "Ожидает"),
                    ("принята", "Принята"),
                    ("отклонена", "Отклонена"),
                    ("забрали", "Забрали"),
                ],
                default="ожидает",
                max_length=20,
            ),
        ),
        migrations.RemoveField(
            model_name="exchangeproposal",
            name="is_active",
        ),
    ]
