# Generated by Django 4.2.16 on 2024-11-25 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracelan', '0019_cooperative_president_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='banner',
            field=models.FileField(blank=True, null=True, upload_to='events/'),
        ),
        migrations.AddField(
            model_name='historicalevent',
            name='banner',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
    ]
