from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from .models import Machine, Mine, Operator, keyPerformanceIndicators, shift, opsum_per_shift, sensor_data
from rest_framework.views import APIView
from .serializers import MachineSerializer, MineSerializer, OperatorSerializer, keyPerformanceIndicatorsSerializer, opsumSerializer, shiftSerializer, sensorSerializer
from datetime import datetime

# Create your views here.
class MachineListCreateView(APIView):
    
    def get(self, request):
        mine = request.query_params.get('mine')
        machines = Machine.objects.all()
        if mine:
            machines = machines.filter(mine=mine)
        serializer = MachineSerializer(machines, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MachineSerializer(data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MineListView(APIView):
    
    def get(self, request):
        name = request.query_params.get('name')
        mines = Mine.objects.all()
        if name:
            mines = mines.filter(name=name)
            serializer = MineSerializer(mines, many = True)
            return Response(serializer.data)
        else:
            return Response("Mine does not exist", status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = MineSerializer(data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteMine(APIView):
    
    def delete(self, request):
        mine = request.query_params.get('name')
        if not mine:
            return Response(
                {"error": "mine parameter is required for deletion."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mines_to_delete = Mine.objects.filter(name=mine)
        if not mines_to_delete.exists():
            return Response(
                {"error": "No mines found for the specified mine."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        mines_to_delete.delete()
        return Response(
            {"message": f"Mine has been deleted successfully."},
            status=status.HTTP_200_OK
        )


class OperatorsView(APIView):
    
    def get(self, request):
        empNo = request.query_params.get('empNo')
        names = Operator.objects.all()
        names = names.filter(employee_number=empNo) if (empNo and empNo != 'all') else names
        if len(names) > 0:
            serializer = OperatorSerializer(names, many = True)
            return Response(serializer.data)
        else:
            return Response("Name does not exist", status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = OperatorSerializer(data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PerformanceIndicatorsView(APIView):

    def get(self, request):

        mine = request.query_params.get('mine')
        performanceIndicators = keyPerformanceIndicators.objects.all()
        if mine:
            performanceIndicators = performanceIndicators.filter(mine=mine)
            serializer = keyPerformanceIndicatorsSerializer(performanceIndicators, many = True)
            return Response(serializer.data)
        else:
            return Response("Mine does not exist", status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = keyPerformanceIndicatorsSerializer(data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            kpi = keyPerformanceIndicators.objects.get(pk=pk)
        except kpi.DoesNotExist:
            return Response(
                {"error": "Mine KPIs undefined."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = keyPerformanceIndicatorsSerializer(kpi, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def find_latest_date(elements):
    latest = max(elements, key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
    return latest

class OPSUMView(APIView):
    
    def get(self, request):
        date = request.query_params.get('date')
        mine = request.query_params.get('mine')
        machine = request.query_params.get('machineID')
        opsumData = opsum_per_shift.objects.all()

        if opsumData:  
            if date == "latest":
                opsumData = opsumData.filter(machine=machine) 
                objLength = len(opsumData)
                opsumData = [opsumData[objLength - 1], opsumData[objLength - 2], opsumData[objLength - 3]]
            else:
                opsumData = opsumData.filter(machine=machine) if (date == "all") else  opsumData.filter(date=date, machine=machine) 
            serializer = opsumSerializer(opsumData, many = True)
            return Response(serializer.data)
    
    def post(self, request):
        opsumDataSerializer = opsumSerializer(data = request.data, many = True)

        # Update the specific_field for a machine with machineID = "123"
        machine = Machine.objects.get(id=request.data[0]['machine'])
        machine.last_seen = request.data[0]['date']
        machine.save()
        
        if opsumDataSerializer.is_valid():
            opsumDataSerializer.save()
            return Response(opsumDataSerializer.data, status=status.HTTP_201_CREATED)
        return Response(opsumDataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SensorView(APIView):
    
    def get(self, request):
        date = request.query_params.get('date')
        mine = request.query_params.get('mine')
        machine = request.query_params.get('machineID')
        sensorData = sensor_data.objects.all()

        if not sensorData.exists():  # Check if the queryset is empty
            return Response("No data found", status=status.HTTP_404_NOT_FOUND)

        if date == "latest":
            sensorData = sensorData#.filter(machine=machine)
            objLength = len(sensorData)
            if objLength >= 3:  # Ensure there are at least 3 objects
                sensorData = [sensorData[objLength - 1], sensorData[objLength - 2], sensorData[objLength - 3]]
            else:
                sensorData = list(sensorData)  # Return all available objects if less than 3
        else:
            sensorData = sensorData.filter(machine=machine) if (date == "all") else sensorData.filter(date=date, machine=machine)

        serializer = sensorSerializer(sensorData, many=True)

        if serializer.data:
            return Response(serializer.data)
        else:
            return Response("No data found for the given filters", status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        sensorDataSerializer = sensorSerializer(data=request.data, many=True)
        print("*******************************")
        
        if sensorDataSerializer.is_valid():
            print("############################")
            sensorDataSerializer.save()
            return Response(sensorDataSerializer.data, status=status.HTTP_201_CREATED)
        return Response(sensorDataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
