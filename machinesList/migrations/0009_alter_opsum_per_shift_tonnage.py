# Generated by Django 5.1.4 on 2025-02-12 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machinesList', '0008_alter_opsum_per_shift_tonnage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opsum_per_shift',
            name='tonnage',
            field=models.IntegerField(),
        ),
    ]
