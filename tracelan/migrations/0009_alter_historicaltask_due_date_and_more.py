# Generated by Django 4.2.16 on 2024-11-22 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracelan', '0008_remove_historicalproject_budget_estimatif_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaltask',
            name='due_date',
            field=models.DateTimeField(verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='historicaltask',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='task',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Start Date'),
        ),
    ]