import os
import re
from bs4 import BeautifulSoup
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, TableStyle, BaseDocTemplate, PageTemplate, Frame, KeepTogether
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.pdfbase import pdfmetrics
from html import unescape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter

# Define the page size and margins
page_width, page_height = letter
left_margin = right_margin = inch
usable_width = page_width - left_margin - right_margin

# Calculate the column widths
first_col_width = usable_width * 0.25  # 1/4 of the usable width
second_col_width = usable_width * 0.75  # 3/4 of the usable width
# Register a Unicode-compatible font
pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'fonts/DejaVuSans-Bold.ttf'))

pdfmetrics.registerFont(TTFont('Arial', 'fonts/Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'fonts/Arial-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'fonts/Arial-Italic.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold-Italic', 'fonts/Arial-Bold-Italic.ttf'))


styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', fontSize=20, fontName='Arial-Bold', spaceAfter=12, alignment=1, textColor=colors.black)
heading_style = ParagraphStyle('Heading', fontSize=18, fontName='Arial-Bold', spaceAfter=12, textColor=colors.black)
subheading_style = ParagraphStyle('Subheading', fontSize=14, fontName='Arial-Bold', spaceAfter=6, textColor=HexColor('#1A76BD'))
tweet_style = ParagraphStyle('Subheading', fontSize=14, fontName='Arial', leading=12, spaceAfter=6, textColor=HexColor('#DA0000'))
normal_style = ParagraphStyle('Normal', fontSize=12, fontName='Arial', leading=12, spaceAfter=6)
all_subheading_style = ParagraphStyle('Heading', fontSize=14, fontName='Arial-Bold', spaceAfter=12, textColor=colors.black)
italic_style = ParagraphStyle('Italic', fontSize=12, fontName='Arial-Italic', leading=12, spaceAfter=6, textColor=colors.darkslategray)
content_style = ParagraphStyle('Content', fontSize=11, fontName='Arial', leading=14, spaceAfter=10)

def csv_to_pdf(folder_path, output_pdf):
    def create_table(df):
        # Create a paragraph style for table cells
        cell_style = ParagraphStyle(
            'CellStyle',
            fontName='DejaVu',
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
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVu-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVu'),
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
    styles['Title'].fontName = 'DejaVu-Bold'
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



def add_header(canvas, doc):
    canvas.saveState()
    
    # Define image paths
    logo_path = "assets/edward-conard-logo.png"
    badge_path = "assets/top-ten-nyt-best-seller-badge.png"
    
    # Calculate positions
    left_image_x = doc.leftMargin
    right_image_x = doc.width - 2 * inch  # Adjust based on your requirement
    
    # Calculate Y position (aligned at the top margin)
    image_y = doc.height + doc.topMargin - 0.5 * inch
    
    # Define width and height for the images
    image_width = 2 * inch
    image_height = 1 * inch  # Adjust based on your requirement
    
    # Add the left image
    canvas.drawImage(logo_path, left_image_x, image_y, width=image_width, height=image_height, preserveAspectRatio=True)
    
    # Add the right image
    canvas.drawImage(badge_path, right_image_x, image_y, width=image_width, height=image_height, preserveAspectRatio=True)
    
    canvas.restoreState()

def clean_html(html_string: str) -> str:
    soup = BeautifulSoup(html_string, 'html.parser')

    # Remove all attributes from tags except for 'href'
    for tag in soup.find_all():
        if 'href' in tag.attrs:
            href_value = tag.attrs['href']
            tag.attrs = {'href': href_value}
        if 'src' in tag.attrs:
            src_value = tag.attrs['src']
            tag.attrs = {'src': src_value}
        else:
            tag.attrs = {}

    # Convert the cleaned HTML back to a string
    cleaned_html = str(soup)
    
    return cleaned_html

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
        doc = BaseDocTemplate(output_pdf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                              leftMargin=0.5 * inch, rightMargin=0.5 * inch)

        frame = Frame(0.5 * inch, 0.5 * inch, doc.width, doc.height, id='normal')
        template = PageTemplate(id='macro_roundup', frames=frame, onPage=add_header)
        doc.addPageTemplates([template])
        # Create the PDF
        # doc = SimpleDocTemplate(output_pdf, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
        #                         leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []

        # Use the CSV filename (without extension) as the title
        title = os.path.splitext(csv_file)[0]
        elements.append(Spacer(1, 24))
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 24))

        for index, row in df.iterrows():
            elements.append(Spacer(1, 24))
            elements.append(Paragraph(f"Article {index + 1}", heading_style))
            elements.append(Spacer(1, 12))

            # Headline and summary
            elements.append(Paragraph(f"<font color='black'>Headline:&nbsp;&nbsp;</font> {str(row['headline'])}", subheading_style))
            elements.append(Spacer(1, 12))
            
            # Publication details
            pub_details = [
                ['Author(s)', row['authors']],
                ['Publication', row['publication']],
                ['Publication Date', row['publication_date']],
            ]
            pub_table = Table(pub_details, colWidths=[first_col_width, second_col_width])
            pub_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ]))
            # Create a KeepTogether flowable
            pub_details_block = KeepTogether([
                pub_table,
                Spacer(1, 12),
            ])

            elements.append(pub_details_block)
            #  Tweet text injection
            tweet_texts = str(row['tweet_text'])
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Tweet:</font></b>" 
                                    f"&nbsp;&nbsp;"
                                    f"<font name='{tweet_style.fontName}' size='{tweet_style.fontSize}' color='{tweet_style.textColor}'>{tweet_texts}</font>", tweet_style))
            elements.append(Spacer(1, 12))

            # Article Summary
            summary = clean_html(str(row['summary']))
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Summary:</font></b>"
                                      f"&nbsp;&nbsp;"
                                      f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{summary}</font>", normal_style))
            elements.append(Spacer(1, 12))
            # Related Articles
            if pd.notna(row['related_articles']):
                related_articles = re.sub(r'\s*style="font-weight:\s*400;"\s*', '', str(row['related_articles']))
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Related Articles:</font></b>"
                                      f"&nbsp;&nbsp;"
                            f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{related_articles}</font>", normal_style))
                
                elements.append(Spacer(1, 12))

            # Topics

            if pd.notna(row['primary_category_name']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Primary Topic:</font></b>"
                                      f"&nbsp;&nbsp;"
                            f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{row['primary_category_name']}</font>", normal_style))
                elements.append(Spacer(1, 12))

            if pd.notna(row['categories']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Topics:</font></b>"
                                      f"&nbsp;&nbsp;"
                                        f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{row['categories']}</font>", normal_style))
                elements.append(Spacer(1, 12))

            if pd.notna(row['pdf_file_url']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>PDF File URL:</font></b>"
                                      f"&nbsp;&nbsp;"
                                        f"<u><font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{row['pdf_file_url']}\">'{row['pdf_file_url']}</a></font></u>", normal_style))
                elements.append(Spacer(1, 12))

            # Links
            if pd.notna(row['permalink']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Permalink:</font></b>"
                                      f"&nbsp;&nbsp;"
                                      f"<u><font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{row['permalink']}\">{row['permalink']}</a></font></u>", normal_style))
                elements.append(Spacer(1, 12))

            if pd.notna(row['featured_image_url']):
            # Featured Image
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Featured Image Link:</font></b>"
                                      f"&nbsp;&nbsp;"
                            f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{row['featured_image_url']}\">{row['featured_image_url']}</a></font>", normal_style))
                elements.append(Spacer(1, 12))

            # SEO Information
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>SEO Title:</font></b>"
                                      f"&nbsp;&nbsp;"
                                    f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{row['seo_title']}</font>", normal_style))
            elements.append(Spacer(1, 12))

            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Meta Description:</font></b> "
                                      f"&nbsp;&nbsp;"
                                    f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{row['meta_description']}</font>", normal_style))
            elements.append(Spacer(1, 12))

            elements.append(PageBreak())

        # Build the PDF
        doc.build(elements)

        print(f"PDF created successfully: {output_pdf}")

        return output_dirs

def remove_html_tags(text):
    """
    Remove HTML tags from a string.

    Args:
        text (str): The input string containing HTML tags.

    Returns:
        str: The string with HTML tags removed.
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

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
        # doc = SimpleDocTemplate(output_pdf, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
        #                         leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        doc = BaseDocTemplate(output_pdf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                              leftMargin=0.5 * inch, rightMargin=0.5 * inch)

        frame = Frame(0.5 * inch, 0.5 * inch, doc.width, doc.height, id='normal')
        template = PageTemplate(id='blog_articles', frames=frame, onPage=add_header)
        doc.addPageTemplates([template])

        elements = []

        elements.append(Spacer(1, 24))
        # Use the CSV filename (without extension) as the title
        title = f"Blog Articles: {os.path.splitext(csv_file)[0]}"
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 24))

        for index, row in df.iterrows():
            elements.append(Spacer(1, 24))
            elements.append(Paragraph(f"Article {index + 1}", heading_style))
            elements.append(Spacer(1, 12))

            # Title
            elements.append(Paragraph(f"Title: {str(row['title'])}", subheading_style))
            elements.append(Spacer(1, 12))
            # Article details
            article_details = [
                ['Author(s)', row['author']],
                ['Publish Date', row['publish_date']],
                ['Publish Time', row['publish_time']],
            ]
            article_table = Table(article_details, colWidths=[first_col_width, second_col_width])
            article_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ]))
            # Create a KeepTogether flowable
            pub_details_block = KeepTogether([
                article_table,
                Spacer(1, 12),
            ])

            elements.append(pub_details_block)

            # Content
            content = remove_html_tags(clean_html(str(row['content'])))
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Content:</font></b>"
                                      f"&nbsp;&nbsp;"
                                    f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{content}</font>", normal_style))
            elements.append(Spacer(1, 12))
            # Primary topic
            if pd.notna(row['primary_category']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Primary Topic:</font></b>"
                                        f"&nbsp;&nbsp;"
                                        f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{row['primary_category']}</font>", normal_style))
                elements.append(Spacer(1, 12))
            # Categories
            if pd.notna(row['categories']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Topics:</font></b> "
                                        f"&nbsp;&nbsp;"
                                        f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{row['categories']}</font>", normal_style))
                elements.append(Spacer(1, 12))

            # Permalink
            if pd.notna(row['permalink']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Permalink:</font></b>"
                                      f"&nbsp;&nbsp;"
                                        f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><u>{row['permalink']}</u></font>", normal_style))
                elements.append(Spacer(1, 12))
            # Featured image

            if pd.notna(row['featured_image_url']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Featured Image Link:</font></b>"
                                      f"&nbsp;&nbsp;"
                                          f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><u><a href=\"{row['featured_image_url']}\">{row['featured_image_url']}</a></u></font>", normal_style)) 
                elements.append(Spacer(1, 12))

            elements.append(PageBreak())

        # Build the PDF
        doc.build(elements)

        print(f"Blog Articles PDF created successfully: {output_pdf}")

        return output_dirs

# class PDF(FPDF):
#     def __init__(self):
#         super().__init__()
#         self.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)
#         self.add_font('DejaVu', 'B', 'fonts/DejaVuSansCondensed-Bold.ttf', uni=True)

#     def header(self):
#         self.set_font('DejaVu', 'B', 12)
#         self.cell(0, 10, 'Title', 0, 1, 'C')

#     def chapter_title(self, title):
#         self.set_font('DejaVu', 'B', 12)
#         self.cell(0, 10, title, 0, 1, 'L')

#     def chapter_body(self, body):
#         self.set_font('DejaVu', '', 12)
#         self.multi_cell(0, 10, body)
#         self.ln()

# def create_pdf(output_pdf, df, title):
#     pdf = PDF()
#     pdf.add_page()
#     pdf.set_title(title)

#     pdf.set_font("DejaVu", 'B', size=24)
#     pdf.set_text_color(0, 0, 128)
#     pdf.cell(0, 10, title, ln=True, align='C')
#     pdf.ln(20)

#     for index, row in df.iterrows():
#         row = row.fillna('')   # Normalize text

#         pdf.set_font("DejaVu", 'B', size=18)
#         pdf.set_text_color(0, 0, 128)
#         pdf.cell(0, 10, f"Article {index + 1}", ln=True)
#         pdf.ln(10)

#         pdf.set_font("DejaVu", 'B', size=14)
#         pdf.set_text_color(0, 100, 0)
#         pdf.multi_cell(0, 10, str(row['headline']))
#         pdf.set_font("DejaVu", '', size=10)
#         pdf.set_text_color(0, 0, 0)
#         pdf.multi_cell(0, 10, f"Summary: {str(row['summary'])}")
#         pdf.ln(10)
#         pdf.multi_cell(0, 10, f"Featured Image Link: {row['featured_image_url']}")
#         pdf.ln(10)

#         pub_details = [
#             f"Publication: {row['publication']}",
#             f"Authors: {row['authors']}",
#             f"Publication Date: {row['publication_date']}",
#             f"Post Date and Time: {row['post_date_and_time']}"
#         ]
#         for detail in pub_details:
#             pdf.cell(0, 10, detail, ln=True)
#         pdf.ln(10)

#         pdf.set_text_color(0, 0, 255)
#         pdf.cell(0, 10, f"Permalink: {row['permalink']}", ln=True, link=row['permalink'])
#         pdf.cell(0, 10, f"PDF File URL: {row['pdf_file_url']}", ln=True, link=row['pdf_file_url'])
#         pdf.ln(10)

#         pdf.set_text_color(0, 0, 0)
#         pdf.cell(0, 10, f"Categories: {row['categories']}", ln=True)
#         pdf.cell(0, 10, f"Primary Category: {row['primary_category_name']}", ln=True)
#         pdf.ln(10)

#         if row['related_articles']:  # Check if related_articles is not empty
#             pdf.set_font("Arial", size=14)
#             pdf.set_text_color(0, 100, 0)
#             pdf.cell(0, 10, "Related Articles:", ln=True)
#             pdf.set_font("Arial", 'I', size=10)
#             pdf.set_text_color(47, 79, 79)
#             pdf.multi_cell(0, 10, str(row['related_articles']))
#             pdf.ln(10)

#         pdf.set_font("Arial", size=14)
#         pdf.set_text_color(0, 100, 0)
#         pdf.cell(0, 10, "SEO Information", ln=True)
#         pdf.set_font("Arial", size=10)
#         pdf.set_text_color(0, 0, 0)
#         pdf.cell(0, 10, f"SEO Title: {row['seo_title']}", ln=True)
#         pdf.cell(0, 10, f"Meta Description: {row['meta_description']}", ln=True)
#         pdf.ln(10)

#         pdf.cell(0, 10, "_" * 80, ln=True)
#         pdf.add_page()

#     pdf.output(output_pdf)

# def macro_roundup_preprocessor(input_dir: str, output_dir: str):
#     if not os.path.isdir(input_dir):
#         return []
    
#     if not os.path.isdir(output_dir):
#         os.makedirs(output_dir)

#     csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

#     output_dirs = []
    
#     if not csv_files:
#         print("No CSV files found in the input directory.")
#         return

#     for csv_file in csv_files:
#         input_file = os.path.join(input_dir, csv_file)
#         output_pdf = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}.pdf")
#         output_dirs.append(output_pdf)

#         df = pd.read_csv(input_file)
#         columns_to_extract = [
#             'headline', 'ID', 'permalink', 'tweet_text', 'post_date_and_time', 'post_date', 'post_time',
#             'summary', 'publication_date', 'order_of_appearance', 'weekly_order_of_appearance',
#             'link', 'authors', 'publication', 'comments', 'featured_image_url', 'extended_excerpt',
#             'pdf_file_id', 'pdf_filename', 'pdf_file_url', 'related_articles', 'categories',
#             'primary_category_name', 'primary_category_has_parent', 'primary_category_parent_name',
#             'is_special_edition', 'special_edition_date', 'special_edition_order_of_appearance',
#             'seo_title', 'meta_description'
#         ]
#         df = df[columns_to_extract]
#         title = os.path.splitext(csv_file)[0]
#         create_pdf(output_pdf, df, title)
#         print(f"PDF created successfully: {output_pdf}")

#     return output_dirs

# def process_blog_articles(input_dir: str, output_dir: str):
#     if not os.path.isdir(input_dir):
#         return []
    
#     if not os.path.isdir(output_dir):
#         os.makedirs(output_dir)

#     csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
#     if not csv_files:
#         print("No CSV files found in the input directory.")
#         return

#     output_dirs = []
#     for csv_file in csv_files:
#         input_file = os.path.join(input_dir, csv_file)
#         output_pdf = os.path.join(output_dir, f"{os.path.splitext(csv_file)[0]}_blog_articles.pdf")
#         output_dirs.append(output_pdf)
        
#         df = pd.read_csv(input_file)
#         columns_to_extract = [
#             'ID', 'title', 'post_status', 'permalink', 'publish_date_and_time', 'publish_date', 
#             'publish_time', 'publish_year', 'author', 'content', 'categories', 'primary_category', 
#             'featured_image_url'
#         ]
#         df = df[columns_to_extract]
#         title = f"Blog Articles: {os.path.splitext(csv_file)[0]}"
#         create_pdf(output_pdf, df, title)
#         print(f"Blog Articles PDF created successfully: {output_pdf}")

#     return output_dirs
