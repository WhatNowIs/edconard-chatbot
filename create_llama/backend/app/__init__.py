import os
import re
import shutil
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

from datetime import datetime

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


def clean_string_for_filename(input_string: str) -> str:
    cleaned_string = re.sub(r'[<>:"/\\|?*\x00-\x1F\']', '_', input_string) 
    
    cleaned_string = re.sub(r'[\s_]+', '_', cleaned_string)

    cleaned_string = cleaned_string.strip().strip('.')

    max_length = 255
    cleaned_string = cleaned_string[:max_length]

    return cleaned_string

def convert_date_format(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    formatted_date = date_obj.strftime('%B %d, %Y')
    
    return formatted_date

def csv_to_pdf(folder_path, output_dir):
    def create_table(df):
        # Create a paragraph style for table cells
        cell_style = ParagraphStyle(
            'CellStyle',
            fontName='Helvetica',  # Adjusted to a default font
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
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Adjusted to a default font
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Adjusted to a default font
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
        print("No CSV files found in the input directory.")
        return

    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'Helvetica-Bold'  # Adjusted to a default font
    styles['Title'].fontSize = 16
    styles['Title'].alignment = 1

    output_files = []

    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)
        output_pdf = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.pdf")
        output_files.append(output_pdf)

        df = pd.read_csv(file_path)

        # Create the PDF document
        doc = SimpleDocTemplate(output_pdf, pagesize=landscape(letter))
        elements = []

        # Add a title for each CSV file
        elements.append(Paragraph(file_name, styles['Title']))
        elements.append(Spacer(1, 0.25*inch))

        # Create and add the table
        table = create_table(df)
        elements.append(table)
        elements.append(Spacer(1, 0.5*inch))

        # Build the PDF
        doc.build(elements)
    # Copy the output files to the data directory
    for output_file in output_files:
        shutil.copy(output_file, "data")

    return output_files

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

def extract_related_article(summary: str):
    if "Related:" in str(summary):
        parts = str(summary).split("Related:")
        modified_summary = parts[0]
        related_article = parts[1]
        
        return modified_summary, related_article
    
    return str(summary), None

from bs4 import BeautifulSoup


def keep_only_anchor_tags(html_string: str) -> str:
    """
    Removes all HTML tags except <a> tags and their content from a given HTML string.
    Also removes unsupported attributes like 'title' from <a> tags.

    Args:
    html_string (str): The HTML string to be cleaned.

    Returns:
    str: The cleaned HTML string with only <a> tags remaining and unsupported attributes removed.
    """
    # Parse the HTML content
    soup = BeautifulSoup(html_string, "html.parser")

    for tag in soup.find_all(True):
        if tag.name != "a":
            tag.unwrap()
        else:
            for attr in list(tag.attrs):
                if attr not in ['href']: 
                    del tag[attr]

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
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Select only the specified columns
        columns_to_extract = [
            'headline', 'permalink', 'tweet_text', 'post_date_and_time',
            'summary', 'publication_date', 'article_link', 'authors', 'publication', 
            'comments', 'is_ai_generated_summary', 'featured_image_url', 'extended_excerpt',
            'pdf_file_url', 'related_articles', 'categories', 'primary_category_name', 'primary_category_has_parent',
            'primary_category_parent_name', 'importance', 'type_of_information', 'source', 'comparisons', 
            'education', 'agreement_sentiment', 'political_perspective', 'timelessness', 'trustworthiness', 
            'seo_title', 'meta_description'
        ]
        df = df[columns_to_extract]

        for _, row in df.iterrows():            
            elements = []

            # Use the CSV filename (without extension) as the title
            file_name = row['headline']
        
            output_pdf = os.path.join(output_dir, f"{clean_string_for_filename(file_name)}.pdf")
            output_dirs.append(output_pdf)


            # Create the PDF
            doc = BaseDocTemplate(output_pdf, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                                leftMargin=0.5 * inch, rightMargin=0.5 * inch)

            frame = Frame(0.5 * inch, 0.5 * inch, doc.width, doc.height, id='normal')
            template = PageTemplate(id='macro_roundup', frames=frame, onPage=add_header)
            doc.addPageTemplates([template])

            elements.append(Spacer(1, 24))
            elements.append(Paragraph(f"Macro Roundup Article", heading_style))
            elements.append(Spacer(1, 12))

            # Headline and summary
            elements.append(Paragraph(f"<font color='black'>Headline:&nbsp;&nbsp;</font> {str(row['headline'])}", subheading_style))
            elements.append(Spacer(1, 12))

            
            # Links
            if pd.notna(row['article_link']):
                elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Article Link:</font></b>"
                                      f"&nbsp;&nbsp;"
                                      f"<u><font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{row['article_link']}\">{row['article_link']}</a></font></u>", normal_style))
                elements.append(Spacer(1, 12))
            
            # Publication details
            pub_details = [
                ['Author(s)', row['authors']],
                ['Publication', row['publication']],
                ['Publication Date', convert_date_format(str(row['publication_date']).split(" ")[0])],
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
            extrated_summary, extracted_related_articles = extract_related_article(row['summary'])
            summary = clean_html(str(extrated_summary))
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Summary:</font></b>"
                                      f"&nbsp;&nbsp;"
                                      f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{summary}</font>", normal_style))
            elements.append(Spacer(1, 12))

            related_article_data = extracted_related_articles if extracted_related_articles != None else str(row['related_articles'])
            # Related Articles
            if pd.notna(related_article_data) and related_article_data.strip():
                related_articles = keep_only_anchor_tags(related_article_data)
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