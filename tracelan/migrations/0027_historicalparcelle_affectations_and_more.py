# Generated by Django 4.2.16 on 2024-11-27 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracelan', '0026_cultureseasonal_cultureperennial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalparcelle',
            name='affectations',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parcelle',
            name='affectations',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parcelle',
            name='culture_perenne',
            field=models.ManyToManyField(blank=True, related_name='cultureperenne', to='tracelan.cultureperennial'),
        ),
        migrations.AddField(
            model_name='parcelle',
            name='culture_saisonniere',
            field=models.ManyToManyField(blank=True, related_name='culturesaison', to='tracelan.cultureseasonal'),
        ),
    ]