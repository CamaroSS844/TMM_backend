# Generated by Django 5.1.4 on 2025-02-03 07:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machinesList', '0004_keyperformanceindicators_fuel_per_shift'),
    ]

    operations = [
        migrations.CreateModel(
            name='sensor_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=1992)),
                ('shift_number', models.IntegerField()),
                ('BW1_FL_Brake_Wear', models.IntegerField()),
                ('BW2_FR_Brake_Wear', models.IntegerField()),
                ('BW3_RL_Brake_Wear', models.IntegerField()),
                ('BW4_RR_Brake_Wear', models.IntegerField()),
                ('BT1_FL_Brake_Temp', models.IntegerField()),
                ('BT1_FR_Brake_Temp', models.IntegerField()),
                ('BT1_RL_Brake_Temp', models.IntegerField()),
                ('BT1_RR_Brake_Temp', models.IntegerField()),
                ('Hoist_Cyl_Len', models.IntegerField()),
                ('Dump_Cyl_Len', models.IntegerField()),
                ('Accelerator_Pedal', models.IntegerField()),
                ('Battery', models.IntegerField()),
                ('Accumulator', models.IntegerField()),
                ('Brake_Return', models.IntegerField()),
                ('Hydraulic_Reflux', models.IntegerField()),
                ('Up_Box_Oil', models.IntegerField()),
                ('Pilot', models.IntegerField()),
                ('Dump_Cyl_Extend', models.IntegerField()),
                ('Dump_Cyl_Retract', models.IntegerField()),
                ('Hoist_Cyl_Extend', models.IntegerField()),
                ('Hoist_Cyl_Retract', models.IntegerField()),
                ('Steering_Cyl_LH_Extend', models.IntegerField()),
                ('Steering_Cyl_RH_Extend', models.IntegerField()),
                ('Service_Brake', models.IntegerField()),
                ('Parking_Brake', models.IntegerField()),
                ('Diesel', models.IntegerField()),
                ('Hydraulic_Oil', models.IntegerField()),
                ('Brake_Cooling_Oil', models.IntegerField()),
                ('machine', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='machinesList.machine')),
                ('mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machinesList.mine')),
            ],
        ),
    ]
