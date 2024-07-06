import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, TableStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bs4 import BeautifulSoup
import re

# Register fonts (adjust paths as needed)
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))

def csv_to_pdf(folder_path, output_pdf):
    def create_table(df):
        # Create a paragraph style for table cells
        cell_style = ParagraphStyle(
            'CellStyle',
            fontName='DejaVuSans',
            fontSize=10,
            leading=12,
            alignment=1  # Center alignment
        )

        # Convert DataFrame to list of lists, wrapping each cell in a Paragraph
        data = [[Paragraph(str(col), cell_style) for col in df.columns]]
        for _, row in df.iterrows():
            data.append([Paragraph(str(cell), cell_style) for cell in row])
        
        # Create the table with automatic width calculation
        table = Table(data, repeatRows=1, colWidths=[None] * len(df.columns))
        
        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ])
        table.setStyle(style)
        return table

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if not csv_files:
        return None
    # Create the PDF document
    doc = SimpleDocTemplate(output_pdf, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'DejaVuSans-Bold'
    styles['Title'].fontSize = 16
    styles['Title'].alignment = 1

    for file_name in csv_files:
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)

            # Add a title for each CSV file
            elements.append(Paragraph(file_name, styles['Title']))
            elements.append(Spacer(1, 0.25*inch))

            # Create and add the table
            table = create_table(df)
            elements.append(table)
            elements.append(Spacer(1, 0.5*inch))

    # Build the PDF
    doc.build(elements)

    return f"PDF with table created successfully: {output_pdf}"

def clean_html(html_content):
    if not isinstance(html_content, str):
        return str(html_content)
    
    # Use BeautifulSoup to parse and clean the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove all tags except for a few basic ones
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    # Get the text content
    text = soup.get_text(separator=' ', strip=True)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Limit the length of the text
    return text[:500] + '...' if len(text) > 500 else text

def csv_blog_to_pdf(csv_dir_path: str, pdf_file_path: str):
    if not os.path.isdir(csv_dir_path):
        raise ValueError(f"The provided path '{csv_dir_path}' is not a directory.")

    csv_files = [f for f in os.listdir(csv_dir_path) if f.endswith('.csv')]
    
    if not csv_files:
        return None

    doc = SimpleDocTemplate(pdf_file_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = ParagraphStyle('Heading2', fontSize=14, fontName='Helvetica-Bold', spaceAfter=6)
    normal_style = ParagraphStyle('Normal', fontSize=10, fontName='Helvetica', leading=12, spaceAfter=6)
    
    elements.append(Paragraph("CSV Data Report", title_style))
    elements.append(Spacer(1, 12))

    for csv_file in csv_files:
        csv_file_path = os.path.join(csv_dir_path, csv_file)
        
        df = pd.read_csv(csv_file_path)
        
        elements.append(Paragraph(f"File: {csv_file}", heading_style))
        elements.append(Spacer(1, 12))
        
        for index, row in df.iterrows():
            elements.append(Paragraph(f"Entry {index + 1}", heading_style))
            elements.append(Spacer(1, 6))
            
            for column in df.columns:
                try:
                    # Clean and convert HTML content to plain text
                    value = clean_html(str(row[column]))
                    # Limit the length of the value to prevent excessively long paragraphs
                    value = value[:1000] + '...' if len(value) > 1000 else value
                    elements.append(Paragraph(f"<b>{column}:</b> {value}", normal_style))
                    elements.append(Spacer(1, 6))
                except Exception as e:
                    print(f"Error processing column {column}: {str(e)}")
                    elements.append(Paragraph(f"<b>{column}:</b> [Error processing content]", normal_style))
                    elements.append(Spacer(1, 6))
            
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("_" * 80, normal_style))  # Separator line
            elements.append(Spacer(1, 12))
        
        # Add a page break after each file
        elements.append(PageBreak())
    
    # Build the PDF
    doc.build(elements)

    return f"PDF created successfully: {pdf_file_path}"