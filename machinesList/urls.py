from django.urls import path, include
from .views import MachineListCreateView, MineListView, DeleteMine, OperatorsView, PerformanceIndicatorsView, OPSUMView, SensorView, GenerateReportView

urlpatterns = [
    path('machinesListCreate/', MachineListCreateView.as_view(), name='machine-list-create'),
    path('createMine/', MineListView.as_view(), name='createMine'),
    path('deleteMine/', DeleteMine.as_view(), name='delete-mine'),
    path('operators/', OperatorsView.as_view(), name='operators'),
    path('kpis/', PerformanceIndicatorsView.as_view(), name='Performance-indicators'),
    path('kpis/<int:pk>/', PerformanceIndicatorsView.as_view(), name='Update-Performance-indicators'),
    path('opsum/', OPSUMView.as_view(), name='operators'),
    path('sensorData/', SensorView.as_view(), name='sensor-data'),
    path('generateReport', GenerateReportView.as_view(), name='generateReport'), # Without trailing slash
    path('generateReport/', GenerateReportView.as_view(), name='generateReport-slash'), # With trailing slash
]
