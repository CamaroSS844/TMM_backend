from django.db import models

# Create your models here.

class Mine(models.Model):
    name = models.CharField(max_length=255, unique=True)
    total_number_of_machines = models.IntegerField()
    number_of_operators = models.IntegerField()
    shift_duration = models.IntegerField()
    
    def __str__(self):
        return f"Mine name{self.name} - No. of Machines {self.total_number_of_machines}"
    
class Machine(models.Model):
    name = models.CharField(max_length=255)
    machine_type = models.CharField(max_length=255)
    id_number = models.CharField(max_length=30, unique=True)
    serial_number = models.CharField(max_length=30, unique=True)
    fleet_number = models.CharField(max_length=30)
    oem = models.CharField(max_length=255)
    year_of_manufacture = models.DateField()
    mine = models.ForeignKey(Mine, to_field='name', on_delete=models.CASCADE)
    last_seen = models.DateField()
    mileage = models.IntegerField()
    operating_hours = models.IntegerField()
    
    def __str__(self):
        return f"Machine name: {self.name} - Mine: {self.mine.name} - Fleet Number: {self.fleet_number}"
    
class Operator(models.Model):
    name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=15, unique=True)
    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    employee_number = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
        return f"Operator name: {self.name} - Mine: {self.mine.name}"
    
class keyPerformanceIndicators(models.Model):
    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    distance_per_shift = models.IntegerField()
    time_per_shift = models.IntegerField()
    machine_type = models.CharField(max_length=255)
    tonnage_per_shift = models.IntegerField()   
    fuel_per_shift = models.IntegerField(default=200)
    
    def __str__(self):
        return f"Machine: {self.machine.name} - Date: {self.date} - OEE: {self.oee}"
    
class shift(models.Model):
    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    date = models.DateField()
    shift_number = models.IntegerField()
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Machine: {self.machine.name} - Date: {self.date} "
    
class opsum_per_shift(models.Model):
    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    shift_number = models.IntegerField()
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, default=1)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, default=1)
    date = models.DateField(default=2020-10-18)
    distance_travelled = models.IntegerField()
    tonnage = models.CharField(max_length=255)
    fuel_consumed = models.IntegerField()
    no_of_loads = models.IntegerField()
    operating_hours = models.IntegerField()
    idle_hours = models.IntegerField()
    engine_hours = models.IntegerField()
    transmission_hours = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'shift_number', 'mine', 'machine'],
                name='unique_machine_shift_date_mine_opsum'
            )
        ]
    
    def __str__(self):
        return f"Machine: {self.machine.name} - Date: {self.date} "
    
    
class sensor_data(models.Model):
    date = models.DateField(default=2020-10-18)
    mine = models.ForeignKey(Mine, on_delete=models.CASCADE)
    shift_number = models.IntegerField()
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, default=1)
    BW1_FL_Brake_Wear = models.IntegerField()
    BW2_FR_Brake_Wear = models.IntegerField()
    BW3_RL_Brake_Wear = models.IntegerField()
    BW4_RR_Brake_Wear = models.IntegerField()
    BT1_FL_Brake_Temp = models.IntegerField()
    BT1_FR_Brake_Temp = models.IntegerField()
    BT1_RL_Brake_Temp = models.IntegerField()
    BT1_RR_Brake_Temp = models.IntegerField()
    Hoist_Cyl_Len = models.IntegerField()
    Dump_Cyl_Len = models.IntegerField()
    Accelerator_Pedal = models.IntegerField()
    Battery = models.IntegerField()
    Accumulator = models.IntegerField()
    Brake_Return = models.IntegerField()
    Hydraulic_Reflux = models.IntegerField()
    Up_Box_Oil = models.IntegerField()
    Pilot = models.IntegerField()
    Dump_Cyl_Extend = models.IntegerField()
    Dump_Cyl_Retract = models.IntegerField()
    Hoist_Cyl_Extend = models.IntegerField()
    Hoist_Cyl_Retract = models.IntegerField()
    Steering_Cyl_LH_Extend = models.IntegerField()
    Steering_Cyl_RH_Extend = models.IntegerField()
    Service_Brake = models.IntegerField()
    Parking_Brake = models.IntegerField()
    Diesel = models.IntegerField()
    Hydraulic_Oil = models.IntegerField()
    Brake_Cooling_Oil = models.IntegerField()
    Transmission_oil = models.IntegerField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'shift_number', 'mine', 'machine'],
                name='unique_sensor_data'
            )
        ]
    
    def __str__(self):
        return f"Machine: {self.machine.name} - Date: {self.date} "
    


# DELETE FROM machinesList_opsum_per_shift
# WHERE id NOT IN (
#     SELECT MIN(id)
#     FROM machinesList_opsum_per_shift
#     GROUP BY shift_number, date, machine_id
# );


