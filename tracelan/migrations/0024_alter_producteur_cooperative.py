# Generated by Django 4.2.16 on 2024-11-26 23:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracelan', '0023_alter_historicalproducteur_date_naissance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producteur',
            name='cooperative',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='producteurs', to='tracelan.cooperative'),
        ),
    ]
