from rest_framework import serializers
from .models import Machine, Mine, Operator, keyPerformanceIndicators, shift, opsum_per_shift, sensor_data

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = "__all__"


class MineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mine
        fields = "__all__"

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = "__all__"

class keyPerformanceIndicatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = keyPerformanceIndicators
        fields = "__all__"

class shiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = shift
        fields = "__all__"

class opsumSerializer(serializers.ModelSerializer):
    class Meta:
        model = opsum_per_shift
        fields = "__all__"


class  sensorSerializer(serializers.ModelSerializer):
    class Meta: 
        model = sensor_data
        fields = "__all__"
