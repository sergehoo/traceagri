# Generated by Django 4.2.16 on 2024-11-26 23:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tracelan', '0024_alter_producteur_cooperative'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cooperative',
            name='code',
            field=models.CharField(default=uuid.uuid4, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='historicalcooperative',
            name='code',
            field=models.CharField(db_index=True, default=uuid.uuid4, max_length=100),
        ),
    ]