from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from .models import Machine, opsum_per_shift
from django.utils.timezone import now
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Sample fleet monitoring data
fleet_data = [
    {"Vehicle ID": "LHD 141", "Mileage (KM)": 3, "Tonnage (T)": 0, "Fuel Consumed (L)": 24, "Violations": 0},
    {"Vehicle ID": "LHD 142", "Mileage (KM)": 0, "Tonnage (T)": 0, "Fuel Consumed (L)": 0, "Violations": 0},
    {"Vehicle ID": "LHD 143", "Mileage (KM)": 0, "Tonnage (T)": 0, "Fuel Consumed (L)": 0, "Violations": 0},
    {"Vehicle ID": "LHD 144", "Mileage (KM)": 0, "Tonnage (T)": 0, "Fuel Consumed (L)": 0, "Violations": 0},
]

# Lightweight AI to analyze data and generate notes
def analyze_data(data):
    notes = []
    total_mileage = sum(record["Mileage (KM)"] for record in data)
    total_tonnage = sum(record["Tonnage (T)"] for record in data)
    total_fuel = sum(record["Fuel Consumed (L)"] for record in data)
    total_violations = sum(record["Violations"] for record in data)

    notes.append(f"Total mileage covered by all vehicles: {total_mileage} KM.")
    notes.append(f"Total tonnage transported: {total_tonnage} T.")
    notes.append(f"Total fuel consumed: {total_fuel} L.")
    notes.append(f"Total violations recorded: {total_violations}.")

    if total_violations == 0:
        notes.append("No violations recorded today. Excellent performance!")
    else:
        notes.append("Review vehicles with violations to improve compliance.")

    if total_fuel > 0:
        efficiency = total_mileage / total_fuel if total_fuel > 0 else 0
        notes.append(f"Overall fuel efficiency: {efficiency:.2f} KM/L.")

    return notes

# Function to generate PDF with graphs
def generate_pdf_v2(data, filename):
    """Generate a PDF report from the given data.
    
    Args:
        data: List of dictionaries containing the report data
        filename: A filename string or a file-like object to write to
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph("Fleet Performance Report", title_style))
    
    # Prepare table data
    headers = ["Vehicle ID", "Mileage (KM)", "Tonnage (T)", "Fuel Consumed (L)", "Violations"]
    table_data = [headers]  # Start with headers
    
    # Add rows
    for item in data:
        row = [
            str(item["Vehicle ID"]),
            str(item["Mileage (KM)"]),
            str(item["Tonnage (T)"]),
            str(item["Fuel Consumed (L)"]),
            str(item["Violations"])
        ]
        table_data.append(row)
    
    # Create table
    table = Table(table_data, repeatRows=1)
    
    # Add style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),  # Navy blue header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
    ])
    table.setStyle(style)
    
    # Add table to elements
    elements.append(table)
    
    # Build PDF
    doc.build(elements)