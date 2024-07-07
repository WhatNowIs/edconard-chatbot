import os
import pandas as pd
import requests
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bs4 import BeautifulSoup

def csv_to_pdf(folder_path, output_pdf):
    def create_table(df):
        # Create a paragraph style for table cells
        cell_style = ParagraphStyle(
            'CellStyle',
            fontName='Helvetica',
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
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
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
    styles['Title'].fontName = 'Helvetica-Bold'
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


def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def fetch_image(url):
    try:
        response = requests.get(url)
        return Image(BytesIO(response.content), width=3*inch, height=2*inch)
    except:
        return None
    
def macro_roundup_preprocessor(input_dir: str, output_dir: str):
    if not os.path.isdir(input_dir):
        return []
    
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

    output_dirs = []
    
    if not csv_files:
        print("No CSV files found in the input directory.")
        return

    for csv_file in csv_files:
        input_file = os.path.join(input_dir, csv_file)
        output_pdf = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}.pdf")
        output_dirs.append(output_pdf)
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Select only the specified columns
        columns_to_extract = [
            'headline', 'ID', 'permalink', 'tweet_text', 'post_date_and_time', 'post_date', 'post_time',
            'summary', 'publication_date', 'order_of_appearance', 'weekly_order_of_appearance',
            'link', 'authors', 'publication', 'comments', 'featured_image_url', 'extended_excerpt',
            'pdf_file_id', 'pdf_filename', 'pdf_file_url', 'related_articles', 'categories',
            'primary_category_name', 'primary_category_has_parent', 'primary_category_parent_name',
            'is_special_edition', 'special_edition_date', 'special_edition_order_of_appearance',
            'seo_title', 'meta_description'
        ]
        df = df[columns_to_extract]

        # Create the PDF
        doc = SimpleDocTemplate(output_pdf, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
                                leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', fontSize=24, fontName='Helvetica-Bold', spaceAfter=12, alignment=1, textColor=colors.darkblue)
        heading_style = ParagraphStyle('Heading', fontSize=18, fontName='Helvetica-Bold', spaceAfter=6, textColor=colors.darkblue)
        subheading_style = ParagraphStyle('Subheading', fontSize=14, fontName='Helvetica-Bold', spaceAfter=6, textColor=colors.darkgreen)
        normal_style = ParagraphStyle('Normal', fontSize=10, fontName='Helvetica', leading=12, spaceAfter=6)
        italic_style = ParagraphStyle('Italic', fontSize=10, fontName='Helvetica-Oblique', leading=12, spaceAfter=6, textColor=colors.darkslategray)

        # Use the CSV filename (without extension) as the title
        title = os.path.splitext(csv_file)[0]
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 24))

        for index, row in df.iterrows():
            elements.append(Paragraph(f"Article {index + 1}", heading_style))
            elements.append(Spacer(1, 12))

            # Headline and summary
            elements.append(Paragraph(clean_html(str(row['headline'])), subheading_style))
            summary = clean_html(str(row['summary']))
            elements.append(Paragraph(f"<b>Summary:</b> {summary}", normal_style))
            elements.append(Spacer(1, 12))

            # Featured Image
            if pd.notna(row['featured_image_url']):
                img = fetch_image(row['featured_image_url'])
                if img:
                    elements.append(img)
                    elements.append(Spacer(1, 12))

            # Publication details
            pub_details = [
                ['Publication', row['publication']],
                ['Authors', row['authors']],
                ['Publication Date', row['publication_date']],
                ['Post Date and Time', row['post_date_and_time']]
            ]
            pub_table = Table(pub_details, colWidths=[1.5*inch, 5*inch])
            pub_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ]))
            elements.append(pub_table)
            elements.append(Spacer(1, 12))

            # Links
            elements.append(Paragraph(f"<b>Permalink:</b> <font color='blue'><u>{row['permalink']}</u></font>", normal_style))
            elements.append(Paragraph(f"<b>PDF File URL:</b> <font color='blue'><u>{row['pdf_file_url']}</u></font>", normal_style))
            elements.append(Spacer(1, 12))

            # Categories
            elements.append(Paragraph(f"<b>Categories:</b> {row['categories']}", normal_style))
            elements.append(Paragraph(f"<b>Primary Category:</b> {row['primary_category_name']}", normal_style))
            elements.append(Spacer(1, 12))

            # Related Articles
            if pd.notna(row['related_articles']):
                elements.append(Paragraph("<b>Related Articles:</b>", subheading_style))
                related_articles = clean_html(str(row['related_articles']))
                elements.append(Paragraph(related_articles, italic_style))
                elements.append(Spacer(1, 12))

            # SEO Information
            elements.append(Paragraph("<b>SEO Information</b>", subheading_style))
            elements.append(Paragraph(f"<b>SEO Title:</b> {row['seo_title']}", normal_style))
            elements.append(Paragraph(f"<b>Meta Description:</b> {row['meta_description']}", normal_style))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("_" * 80, normal_style))  # Separator line
            elements.append(PageBreak())

        # Build the PDF
        doc.build(elements)

        print(f"PDF created successfully: {output_pdf}")

        return output_dirs

def process_blog_articles(input_dir: str, output_dir: str):
    if not os.path.isdir(input_dir):
        return []
    
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the input directory.")
        return

    output_dirs = []
    for csv_file in csv_files:
        input_file = os.path.join(input_dir, csv_file)
        output_pdf = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}_blog_articles.pdf")
        output_dirs.append(output_pdf)
        
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Select only the specified columns
        columns_to_extract = [
            'ID', 'title', 'post_status', 'permalink', 'publish_date_and_time', 'publish_date', 
            'publish_time', 'publish_year', 'author', 'content', 'categories', 'primary_category', 
            'featured_image_url'
        ]
        df = df[columns_to_extract]

        # Create the PDF
        doc = SimpleDocTemplate(output_pdf, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
                                leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', fontSize=24, fontName='Helvetica-Bold', spaceAfter=12, alignment=1, textColor=colors.darkblue)
        heading_style = ParagraphStyle('Heading', fontSize=18, fontName='Helvetica-Bold', spaceAfter=6, textColor=colors.darkblue)
        subheading_style = ParagraphStyle('Subheading', fontSize=14, fontName='Helvetica-Bold', spaceAfter=6, textColor=colors.darkgreen)
        normal_style = ParagraphStyle('Normal', fontSize=10, fontName='Helvetica', leading=12, spaceAfter=6)
        content_style = ParagraphStyle('Content', fontSize=11, fontName='Helvetica', leading=14, spaceAfter=10)

        # Use the CSV filename (without extension) as the title
        title = f"Blog Articles: {os.path.splitext(csv_file)[0]}"
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 24))

        for index, row in df.iterrows():
            elements.append(Paragraph(f"Article {index + 1}", heading_style))
            elements.append(Spacer(1, 12))

            # Title
            elements.append(Paragraph(clean_html(str(row['title'])), subheading_style))
            elements.append(Spacer(1, 12))

            # Featured Image
            if pd.notna(row['featured_image_url']):
                img = fetch_image(row['featured_image_url'])
                if img:
                    elements.append(img)
                    elements.append(Spacer(1, 12))

            # Article details
            article_details = [
                ['ID', str(row['ID'])],
                ['Author', row['author']],
                ['Publish Date', row['publish_date']],
                ['Publish Time', row['publish_time']],
                ['Publish Year', str(row['publish_year'])],
                ['Post Status', row['post_status']]
            ]
            article_table = Table(article_details, colWidths=[1.5*inch, 5*inch])
            article_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ]))
            elements.append(article_table)
            elements.append(Spacer(1, 12))

            # Permalink
            elements.append(Paragraph(f"<b>Permalink:</b> <font color='blue'><u>{row['permalink']}</u></font>", normal_style))
            elements.append(Spacer(1, 12))

            # Categories
            elements.append(Paragraph(f"<b>Categories:</b> {row['categories']}", normal_style))
            elements.append(Paragraph(f"<b>Primary Category:</b> {row['primary_category']}", normal_style))
            elements.append(Spacer(1, 12))

            # Content
            elements.append(Paragraph("<b>Content:</b>", subheading_style))
            content = clean_html(str(row['content']))
            elements.append(Paragraph(content[:1000] + "..." if len(content) > 1000 else content, content_style))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph("_" * 80, normal_style))
            elements.append(PageBreak())

        # Build the PDF
        doc.build(elements)

        print(f"Blog Articles PDF created successfully: {output_pdf}")

        return output_dirs