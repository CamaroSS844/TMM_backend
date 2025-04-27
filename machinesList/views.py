from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from rest_framework.response import Response
from rest_framework import status
from .models import Machine, Mine, Operator, keyPerformanceIndicators, shift, opsum_per_shift, sensor_data
from rest_framework.views import APIView
from .serializers import MachineSerializer, MineSerializer, OperatorSerializer, keyPerformanceIndicatorsSerializer, opsumSerializer, shiftSerializer, sensorSerializer
from datetime import datetime
import pandas as pd
from django.core.cache import cache
from django.utils import timezone
import threading
import time
import io
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import xlsxwriter
from django.template.loader import render_to_string
import os
from .testPDF_Script import generate_pdf_v2

# Create your views here.
class MachineListCreateView(APIView):
    def get(self, request):
        mine_param = request.query_params.get('mine')
        machines = Machine.objects.all()
        
        if mine_param:
            try:
                if mine_param.isdigit():
                    # Try to get mine by ID first
                    mine = Mine.objects.get(id=mine_param)
                else:
                    # If not a number, treat as mine name
                    mine = Mine.objects.get(name=mine_param)
                machines = machines.filter(mine=mine)
            except Mine.DoesNotExist:
                return Response(
                    {"error": f"Mine with identifier '{mine_param}' not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MachineSerializer(data=request.data)
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

def generate_opsum_report():
    """Generate OPSUM reports and store in cache"""
    while True:
        print("\n====== Starting OPSUM Report Generation ======")
        try:
            # Get all OPSUM data and all machines
            opsumData = opsum_per_shift.objects.all()
            all_machines = Machine.objects.all()
            
            # Get latest date data
            latestDate = opsum_per_shift.objects.latest('date').date
            latest_data = opsumData.filter(date=latestDate)
            print(f"\nProcessing data for date: {latestDate}")
            
            # Convert to DataFrame and generate summary
            df = pd.DataFrame(list(latest_data.values()))
            
            if not df.empty:
                # Ensure tonnage is float
                df['tonnage'] = df['tonnage'].astype(float)
                print("\nTonnage values before grouping:")
                for _, row in df.iterrows():
                    print(f"Machine {row['machine_id']}: {row['tonnage']}")
                
                summary = df.groupby("machine_id").agg(
                    tonnage=pd.NamedAgg(column="tonnage", aggfunc="sum"),
                    fuel_consumed=pd.NamedAgg(column="fuel_consumed", aggfunc="sum"),
                    distance_travelled=pd.NamedAgg(column="distance_travelled", aggfunc="sum"),
                    date=pd.NamedAgg(column="date", aggfunc="min")
                ).reset_index()
                
                print("\nTonnage sums after grouping:")
                for _, row in summary.iterrows():
                    print(f"Machine {row['machine_id']} total tonnage: {row['tonnage']}")
            else:
                # Create empty summary with machine_id column
                summary = pd.DataFrame(columns=['machine_id', 'tonnage', 'fuel_consumed', 'distance_travelled', 'date'])
            
            # Create DataFrame with all machines
            all_machines_df = pd.DataFrame(list(all_machines.values('id', 'fleet_number')))
            all_machines_df.columns = ['machine_id', 'machine_name']
            print("\nAll machines DataFrame:", all_machines_df.to_string())
            
            # Merge with summary to include all machines
            final_summary = pd.merge(
                all_machines_df,
                summary,
                on='machine_id',
                how='left'
            )
            
            # Fill NaN values with 0 and the latest date
            final_summary['tonnage'] = final_summary['tonnage'].fillna(0)
            final_summary['fuel_consumed'] = final_summary['fuel_consumed'].fillna(0)
            final_summary['distance_travelled'] = final_summary['distance_travelled'].fillna(0)
            final_summary['date'] = final_summary['date'].fillna(latestDate)
            
            # Convert to dict and store in cache
            report_data = final_summary.to_dict(orient="records")
            cache.set('opsum_report', report_data, timeout=120)  # Cache for 2 minutes
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            
        time.sleep(20)  # Wait for 20 seconds before next update

# Start the background thread when Django starts
report_thread = threading.Thread(target=generate_opsum_report, daemon=True)
report_thread.start()

class OPSUMView(APIView):
    def get(self, request):
        date = request.query_params.get('date')
        mine = request.query_params.get('mine')
        machine = request.query_params.get('machineID')
        
        if date == "latest":
            # Get cached report
            cached_report = cache.get('opsum_report')
            if cached_report:
                return Response(cached_report)
            
            # If cache missed, generate report
            opsumData = opsum_per_shift.objects.all()
            latestDate = opsum_per_shift.objects.latest('date').date
            opsumData = opsumData.filter(date=latestDate)
            
            df = pd.DataFrame(list(opsumData.values()))
            if not df.empty:
                # Convert tonnage to float before aggregation
                df['tonnage'] = df['tonnage'].astype(float)
                
                summary = df.groupby("machine_id").agg(
                    tonnage=pd.NamedAgg(column="tonnage", aggfunc="sum"),
                    fuel_consumed=pd.NamedAgg(column="fuel_consumed", aggfunc="sum"),
                    distance_travelled=pd.NamedAgg(column="distance_travelled", aggfunc="sum"),
                    date=pd.NamedAgg(column="date", aggfunc="min")
                ).reset_index()
                
                opsumData = summary.to_dict(orient="records")
                return Response(opsumData)
            return Response([])  # Return empty list if no data
        
        else:
            opsumData = opsum_per_shift.objects.all()
            opsumData = opsumData.filter(machine=machine) if (date == "all") else opsumData.filter(date=date, machine=machine)
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
        
        if sensorDataSerializer.is_valid():
            sensorDataSerializer.save()
            return Response(sensorDataSerializer.data, status=status.HTTP_201_CREATED)
        return Response(sensorDataSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

def background_report_generator():
    """Background task to generate reports periodically"""
    while True:
        try:
            # Generate and store the PDF report
            buffer = io.BytesIO()
            latest_date = opsum_per_shift.objects.latest('date').date
            opsum_data = opsum_per_shift.objects.filter(date=latest_date)
            machines = Machine.objects.all()
            
            # Prepare data for the report in the format expected by generate_pdf_v2
            report_data = []
            for machine in machines:
                machine_data = opsum_data.filter(machine=machine)
                mileage = sum(item.distance_travelled for item in machine_data)
                tonnage = sum(item.tonnage for item in machine_data)
                fuel_consumed = sum(item.fuel_consumed for item in machine_data)
                violations = 0  # You can implement this based on your business logic
                
                report_data.append({
                    "Vehicle ID": machine.fleet_number,
                    "Mileage (KM)": mileage,
                    "Tonnage (T)": tonnage,
                    "Fuel Consumed (L)": fuel_consumed,
                    "Violations": violations,
                })
            
            generate_pdf_v2(report_data, filename=buffer)
            buffer.seek(0)
            
            # Store both the raw data and PDF in cache
            cache.set('report_data', report_data, timeout=3600)  # Cache for 1 hour
            cache.set('latest_report_pdf', buffer.getvalue(), timeout=3600)
            print("Report generated and cached successfully.")
        except Exception as e:
            print(f"Error generating report: {e}")
        
        time.sleep(1800)  # Run every 30 minutes

# Start the background thread when Django starts
report_thread = threading.Thread(target=background_report_generator, daemon=True)
report_thread.start()

class GenerateReportView(APIView):
    def get(self, request):
        format_type = request.query_params.get('format', 'excel').lower()
        if format_type not in ['pdf', 'excel']:
            return Response(
                {"error": "Invalid format. Use 'pdf' or 'excel'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            report_data = cache.get('report_data')
            if not report_data:
                latest_date = opsum_per_shift.objects.latest('date').date
                opsum_data = opsum_per_shift.objects.filter(date=latest_date)
                machines = Machine.objects.all()
                
                # Create DataFrame with all machines first
                all_machines_df = pd.DataFrame(list(machines.values('id', 'fleet_number')))
                all_machines_df.columns = ['machine_id', 'machine_name']
                
                if opsum_data.exists():
                    df = pd.DataFrame(list(opsum_data.values()))
                    df['tonnage'] = df['tonnage'].astype(float)
                    
                    # Group by machine_id and calculate metrics
                    summary = df.groupby("machine_id").agg(
                        tonnage=pd.NamedAgg(column="tonnage", aggfunc="sum"),
                        fuel_consumed=pd.NamedAgg(column="fuel_consumed", aggfunc="sum"),
                        distance_travelled=pd.NamedAgg(column="distance_travelled", aggfunc="sum"),
                        date=pd.NamedAgg(column="date", aggfunc="min")
                    ).reset_index()
                else:
                    # Create empty summary DataFrame with required columns
                    summary = pd.DataFrame(columns=['machine_id', 'tonnage', 'fuel_consumed', 'distance_travelled', 'date'])
                
                # Merge with all machines to include those without data
                final_summary = pd.merge(
                    all_machines_df,
                    summary,
                    on='machine_id',
                    how='left'
                )
                
                # Fill NaN values with 0 and latest date
                final_summary['tonnage'] = final_summary['tonnage'].fillna(0.0)
                final_summary['fuel_consumed'] = final_summary['fuel_consumed'].fillna(0)
                final_summary['distance_travelled'] = final_summary['distance_travelled'].fillna(0)
                final_summary['date'] = final_summary['date'].fillna(latest_date)
                
                report_data = final_summary.to_dict(orient="records")
                cache.set('report_data', report_data, timeout=3600)

            buffer = io.BytesIO()
            
            if format_type == 'pdf':
                try:
                    generate_pdf_v2(report_data, filename=buffer)
                    buffer.seek(0)
                    response = FileResponse(
                        buffer,
                        as_attachment=True,
                        filename='fleet_report.pdf'
                    )
                    response['Content-Type'] = 'application/pdf'
                    response['Content-Disposition'] = 'attachment; filename="fleet_report.pdf"'
                    return response
                except Exception as e:
                    return Response(
                        {"error": f"Error generating PDF: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            else:  # excel format
                workbook = xlsxwriter.Workbook(buffer)
                worksheet = workbook.add_worksheet()
                
                # Add title with formatting
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'center',
                    'valign': 'vcenter'
                })
                worksheet.merge_range('A1:E1', 'Fleet Performance Report', title_format)
                
                # Add headers with formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#000080',
                    'font_color': 'white'
                })
                headers = ["Vehicle ID", "Mileage (KM)", "Tonnage (T)", "Fuel Consumed (L)", "Violations"]
                for col, header in enumerate(headers):
                    worksheet.write(1, col, header, header_format)
                
                # Add data
                for row, item in enumerate(report_data, start=2):
                    for col, header in enumerate(headers):
                        worksheet.write(row, col, item[header])
                
                workbook.close()
                buffer.seek(0)
                
                response = FileResponse(
                    buffer,
                    as_attachment=True,
                    filename='fleet_report.xlsx'
                )
                response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                response['Content-Disposition'] = 'attachment; filename="fleet_report.xlsx"'
                return response

        except Exception as e:
            return Response(
                {"error": f"Error generating report: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

