# Generated by Django 5.1.4 on 2025-02-10 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machinesList', '0006_sensor_data_transmission_oil'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='sensor_data',
            constraint=models.UniqueConstraint(fields=('date', 'shift_number', 'mine'), name='unique_fields'),
        ),
    ]
