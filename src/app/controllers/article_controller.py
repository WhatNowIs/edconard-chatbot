from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Generator
import os
import gc
import logging
import shutil
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.schema import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage import StorageContext
from create_llama.backend.app.engine.loaders.file import FileLoaderConfig, get_file_documents
from create_llama.backend.app.engine.vectordb import get_vector_store
from src.utils.logger import get_logger
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from llama_index.core.settings import Settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Spacer, Frame, PageTemplate, BaseDocTemplate, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, black, darkslategray
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd

load_dotenv()

logger = get_logger()

# Configure logging
logger = logging.getLogger(__name__)

# Constants for memory management
MAX_BATCH_SIZE = 1000  # Reduced batch size to prevent memory issues
GC_THRESHOLD = 5000    # Nodes before forcing garbage collection
CHUNK_SIZE = 1024      # Default chunk size for text splitting
CHUNK_OVERLAP = 20     # Default chunk overlap

project_root = Path(__file__).parent.parent.parent.parent
# Constants for directories
STORAGE_DIR = os.path.join(project_root, 'storage')
ASSETS_DIR = os.path.join(project_root, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
LOGOS_DIR = ASSETS_DIR
STORAGE_PDFS_DIR = os.path.join(project_root, 'data')

# Configure Settings
Settings.chunk_size = CHUNK_SIZE
Settings.chunk_overlap = CHUNK_OVERLAP


def ensure_directories():
    """Ensure all required directories exist"""
    try:
        # Create directories if they don't exist
        os.makedirs(STORAGE_DIR, exist_ok=True)
        os.makedirs(FONTS_DIR, exist_ok=True)
        os.makedirs(LOGOS_DIR, exist_ok=True)
        os.makedirs(STORAGE_PDFS_DIR, exist_ok=True)
        
        # Log directory creation
        logger.info(f"Storage directory: {STORAGE_DIR}")
        logger.info(f"Fonts directory: {FONTS_DIR}")
        logger.info(f"Logos directory: {LOGOS_DIR}")
        logger.info(f"PDFs directory: {STORAGE_PDFS_DIR}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {str(e)}")
        return False

def check_required_assets():
    """Check if all required assets are present"""
    required_fonts = [
        ('Arial.ttf', 'Arial Regular'),
        ('Arial-Bold.ttf', 'Arial Bold'),
        ('Arial-Italic.ttf', 'Arial Italic'),
        ('DejaVuSans.ttf', 'DejaVu Regular'),
        ('DejaVuSans-Bold.ttf', 'DejaVu Bold'),
        ('DejaVuSans-Oblique.ttf', 'DejaVu Italic')
    ]
    
    required_logos = [
        ('edward-conard-logo.png', 'Edward Conard Logo'),
        ('top-ten-nyt-best-seller-badge.png', 'NYT Best Seller Badge')
    ]
    
    missing_assets = []
    
    # Check fonts
    for font_file, font_name in required_fonts:
        if not os.path.exists(os.path.join(FONTS_DIR, font_file)):
            missing_assets.append(f"Missing font: {font_name} ({font_file})")
    
    # Check logos
    for logo_file, logo_name in required_logos:
        if not os.path.exists(os.path.join(LOGOS_DIR, logo_file)):
            missing_assets.append(f"Missing logo: {logo_name} ({logo_file})")
    
    if missing_assets:
        logger.warning("Missing required assets:")
        for asset in missing_assets:
            logger.warning(f"  - {asset}")
        return False
    
    logger.info("All required assets are present")
    return True

# Initialize on module import
if not ensure_directories():
    logger.error("Failed to create required directories")

if not check_required_assets():
    logger.warning("Some required assets are missing, PDFs may not display correctly")

# Font file paths
arial_regular = os.path.join(FONTS_DIR, 'Arial.ttf')
arial_bold = os.path.join(FONTS_DIR, 'Arial-Bold.ttf')
arial_italic = os.path.join(FONTS_DIR, 'Arial-Italic.ttf')
dejavu_regular = os.path.join(FONTS_DIR, 'DejaVuSans.ttf')
dejavu_bold = os.path.join(FONTS_DIR, 'DejaVuSans-Bold.ttf')
dejavu_italic = os.path.join(FONTS_DIR, 'DejaVuSans-Oblique.ttf')

# Font registration function
def register_fonts():
    """Register all required fonts for PDF generation"""
    try:
        # Register Arial fonts
        pdfmetrics.registerFont(TTFont('Arial', arial_regular))
        pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold))
        pdfmetrics.registerFont(TTFont('Arial-Italic', arial_italic))
        
        # Register DejaVu fonts
        pdfmetrics.registerFont(TTFont('DejaVu', dejavu_regular))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', dejavu_bold))
        pdfmetrics.registerFont(TTFont('DejaVu-Italic', dejavu_italic))
        
        # Register font families
        pdfmetrics.registerFontFamily(
            'Arial',
            normal='Arial',
            bold='Arial-Bold',
            italic='Arial-Italic'
        )
        
        pdfmetrics.registerFontFamily(
            'DejaVu',
            normal='DejaVu',
            bold='DejaVu-Bold',
            italic='DejaVu-Italic'
        )
        
        logger.info("Successfully registered all fonts")
        return True
    except Exception as e:
        logger.error(f"Error registering fonts: {str(e)}")
        return False

# Register fonts on module import
if not register_fonts():
    logger.warning("Font registration failed, PDFs may not display correctly")

# Define the page size and margins
page_width, page_height = letter
left_margin = right_margin = inch
usable_width = page_width - left_margin - right_margin

# Calculate the column widths
first_col_width = usable_width * 0.25  # 1/4 of the usable width
second_col_width = usable_width * 0.75  # 3/4 of the usable width

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'Title',
    fontName='Arial-Bold',
    fontSize=20,
    alignment=1,  # Center alignment
    textColor=colors.black,
    spaceAfter=0.2*inch
)

heading_style = ParagraphStyle(
    'Heading',
    fontName='Arial-Bold',
    fontSize=18,
    textColor=colors.black,
    spaceAfter=0.2*inch
)

subheading_style = ParagraphStyle(
    'Subheading',
    fontName='Arial-Bold',
    fontSize=14,
    textColor=HexColor('#1A76BD'),  # Blue color
    spaceAfter=0.1*inch
)

tweet_style = ParagraphStyle(
    'Tweet',
    fontName='Arial',
    fontSize=14,
    textColor=HexColor('#DA0000'),  # Red color
    spaceAfter=0.2*inch,
    leading=16  # Increased line spacing for readability
)

normal_style = ParagraphStyle(
    'Normal',
    fontName='Arial',
    fontSize=12,
    textColor=colors.black,
    spaceAfter=0.1*inch,
    leading=14
)

content_style = ParagraphStyle(
    'Content',
    fontName='Arial',
    fontSize=11,
    textColor=colors.black,
    spaceAfter=0.1*inch,
    leading=13
)

italic_style = ParagraphStyle(
    'Italic',
    fontName='Arial-Italic',
    fontSize=12,
    textColor=colors.darkslategray,
    spaceAfter=0.1*inch,
    leading=14
)

# Define table styles
table_style = TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Arial-Bold'),  # First column headers in bold
    ('FONTNAME', (1, 0), (-1, -1), 'Arial'),      # Content in regular
    ('FONTSIZE', (0, 0), (-1, -1), 11),           # All text 11pt
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
])

# Table for article details
details_table_style = TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Arial-Bold'),  # First column headers in bold
    ('FONTNAME', (1, 0), (-1, -1), 'Arial'),      # Content in regular
    ('FONTSIZE', (0, 0), (-1, -1), 11),           # All text 11pt
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.lightgrey, colors.white]),
])

class Article(BaseModel):
    """Article model with required fields"""
    headline: str
    article_link: str
    authors: str
    publication: str
    publication_date: str
    summary: Optional[str] = None
    tweet: Optional[str] = None
    permalink: str
    featured_image_url: Optional[str] = None
    primary_category_name: str
    categories: list[str]
    related_articles: Optional[list[dict[str, str]]] = None  # List of dicts with 'title' and 'link'
    source: Optional[str] = None
    pdf_file_url: Optional[str] = None
    extended_excerpt: Optional[str] = None

class ArticleUploadResponse(BaseModel):
    message: str
    status: str = "success"
    processed_count: int
    error_count: int
    pdf_paths: List[str]

router = APIRouter()

def convert_date_format(date_str: str) -> str:
    """Convert date string to desired format"""
    try:
        if not date_str or date_str.lower() in ["nan", "none", "null"]:
            return "Unknown"
        # Handle date format from payload: "2/14/2025 0:00"
        date_obj = datetime.strptime(date_str.strip(), "%m/%d/%Y %H:%M")
        return date_obj.strftime("%B %d, %Y")
    except ValueError as e:
        logger.warning(f"Error parsing date '{date_str}': {str(e)}")
        return date_str

def clean_html(html_str: str) -> str:
    """Clean HTML string"""
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text()

def add_header(canvas, doc):
    """Add header with logos to each page"""
    canvas.saveState()
    
    # Calculate header height and positions
    header_height = 0.75 * inch
    header_top = doc.height + doc.topMargin
    header_bottom = header_top - header_height
    
    # Left logo - edward-conard-logo.png
    left_logo = os.path.join(LOGOS_DIR, 'edward-conard-logo.png')
    if os.path.exists(left_logo):
        canvas.drawImage(
            left_logo,
            doc.leftMargin,
            header_bottom,
            width=2*inch,
            height=header_height,
            preserveAspectRatio=True,
            mask='auto'
        )
    else:
        logger.warning(f"Left logo not found: {left_logo}")
        canvas.setFont('Arial-Bold', 12)
        canvas.drawString(doc.leftMargin, header_bottom + 0.25*inch, "EDWARD CONARD")
    
    # Right logo - top-ten-nyt-best-seller-badge.png
    right_logo = os.path.join(LOGOS_DIR, 'top-ten-nyt-best-seller-badge.png')
    if os.path.exists(right_logo):
        # Right logo is square, so use header_height for both dimensions
        canvas.drawImage(
            right_logo,
            doc.width - header_height,
            header_bottom,
            width=header_height,
            height=header_height,
            preserveAspectRatio=True,
            mask='auto'
        )
    else:
        logger.warning(f"Right logo not found: {right_logo}")
        canvas.setFont('Arial-Bold', 12)
        canvas.drawString(doc.width - 2*inch, header_bottom + 0.25*inch, "TOP TEN NYT BESTSELLER")
    
    # Draw a line under the header
    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, header_bottom - 0.1*inch, doc.width, header_bottom - 0.1*inch)
    
    canvas.restoreState()

def create_pipeline(vector_store) -> IngestionPipeline:
    """Create ingestion pipeline with specified settings"""
    try:
        ensure_directories()
        
        return IngestionPipeline(
            transformations=[
                SentenceSplitter(
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP
                ),
                Settings.embed_model,
            ],
            vector_store=vector_store,
            docstore_strategy="upserts"  # Ensure upserts strategy is used
        )
    except Exception as e:
        logger.error(f"Error creating pipeline: {str(e)}")
        raise

def process_batch(pipeline: IngestionPipeline, docs: List[Document], current: int, total: int) -> List[Document]:
    """Process a batch of documents with comprehensive logging"""
    try:
        logger.info(f"Processing batch {current}/{total}")
        processed_docs = pipeline.run(docs)
        logger.info(f"Successfully processed batch {current}/{total}")
        return processed_docs
    except Exception as e:
        logger.error(f"Error processing batch {current}/{total}: {str(e)}")
        return []

def process_article_batch(articles: List[Article], vector_store) -> bool:
    """Process a batch of articles and add them to the vector store"""
    try:
        total_articles = len(articles)
        logger.info(f"Processing {total_articles} articles with memory management settings - Batch size: {MAX_BATCH_SIZE}, GC threshold: {GC_THRESHOLD}")
        
        # Create pipeline with vector store and sentence splitter
        pipeline = create_pipeline(vector_store)
        
        successful_articles = 0
        failed_articles = 0
        node_count = 0
        
        for batch_start in range(0, total_articles, MAX_BATCH_SIZE):
            batch_end = min(batch_start + MAX_BATCH_SIZE, total_articles)
            batch = articles[batch_start:batch_end]
            
            for i, article in enumerate(batch, start=batch_start):
                try:
                    # Generate PDF
                    pdf_path = os.path.join(STORAGE_PDFS_DIR, f"{clean_filename(article.headline)}.pdf")
                    
                    if generate_pdf(article, pdf_path):
                        logger.info(f"Generated PDF for article {i+1}/{total_articles}: {article.headline}")
                        
                        try:
                            # Get documents using get_file_documents with configurable chunk size
                            config = FileLoaderConfig(
                                data_dir=STORAGE_PDFS_DIR,
                                chunk_size=CHUNK_SIZE,
                                chunk_overlap=CHUNK_OVERLAP
                            )
                            docs = get_file_documents(config)
                            
                            if not docs:
                                logger.warning(f"No documents found for article {i+1}")
                                failed_articles += 1
                                continue
                            
                            # Process documents and update node count
                            processed_docs = process_batch(pipeline, docs, i+1, total_articles)
                            if processed_docs:
                                node_count += len(processed_docs)
                                successful_articles += 1
                            else:
                                failed_articles += 1
                                continue
                            
                            # Force garbage collection if needed
                            if node_count >= GC_THRESHOLD:
                                gc.collect()
                                logger.info(f"Memory cleanup - Processed {node_count} nodes, forcing garbage collection")
                                node_count = 0
                            
                        except Exception as e:
                            logger.error(f"Error processing documents for article {i+1}: {str(e)}")
                            failed_articles += 1
                            continue
                    else:
                        logger.error(f"Failed to generate PDF for article {i+1}")
                        failed_articles += 1
                        continue
                        
                except Exception as e:
                    logger.error(f"Error processing article {i+1}: {str(e)}")
                    failed_articles += 1
                    continue
        
        # Log final statistics
        logger.info(f"Batch processing complete - Successful: {successful_articles}, Failed: {failed_articles}, Total: {total_articles}")
        return True
        
    except Exception as e:
        logger.error(f"Error in process_article_batch: {str(e)}")
        return False

def cleanup_storage():
    """Clean up vector store collections"""
    try:
        logger.info("Starting storage cleanup...")
        
        # Clean up Qdrant collections
        vector_store = get_vector_store()
        vector_store.delete_collection()
        logger.info("Deleted vector store collections")
        
        # Ensure PDF storage directory exists
        ensure_directories()
        logger.info("Ensured PDF storage directory exists")
        
        return True
    except Exception as e:
        logger.error(f"Error during storage cleanup: {str(e)}")
        return False

@router.post("/reset")
async def reset_storage():
    """Reset vector store collections"""
    try:
        if cleanup_storage():
            return {"message": "Successfully reset vector store"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset vector store")
    except Exception as e:
        logger.error(f"Error in reset_storage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_article_files(articles: List[Article]):
    """Upload and process article files, adding them to the vector store"""
    try:
        total_articles = len(articles)
        logger.info(f"Starting upload of {total_articles} articles")
        
        # Get vector store instance
        vector_store = get_vector_store()
        
        # Process articles in batches
        for batch_start in range(0, total_articles, MAX_BATCH_SIZE):
            batch_end = min(batch_start + MAX_BATCH_SIZE, total_articles)
            batch = articles[batch_start:batch_end]
            
            if not process_article_batch(batch, vector_store):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process batch starting at {batch_start}"
                )
        
        return {"message": f"Successfully processed {total_articles} articles"}
        
    except Exception as e:
        logger.error(f"Error in upload_article_files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def clean_filename(text: str) -> str:
    """Clean text to be used as a filename"""
    import re
    # Replace invalid characters and spaces
    text = re.sub(r'[<>:"/\\|?*\s]', '_', text)
    # Remove multiple underscores
    text = re.sub(r'_+', '_', text)
    # Limit length and remove trailing underscores
    return text[:50].strip('_')

def generate_pdf(article: Article, output_path: str):
    """Generate a PDF with consistent formatting for an article."""
    try:
        # Ensure fonts are registered
        if not register_fonts():
            raise Exception("Required fonts are not available")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create the PDF with proper margins
        doc = BaseDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=1.5*inch,  # 1.5 inch top margin as specified
            bottomMargin=inch
        )
        
        # Create page template with header
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id='normal'
        )
        template = PageTemplate(id='macro_roundup', frames=frame, onPage=add_header)
        doc.addPageTemplates([template])
        
        elements = []
        
        # Title section
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(clean_html(article.headline), title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Key Takeaway section
        if article.tweet:
            elements.append(Paragraph("Key Takeaway", heading_style))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(clean_html(article.tweet), tweet_style))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Article Details section
        elements.append(Paragraph("Article Details", heading_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Publication details in a structured format
        pub_details = [
            ['Author(s)', clean_html(article.authors)],
            ['Publication', clean_html(article.publication)],
            ['Publication Date', convert_date_format(article.publication_date)],
            ['Source', clean_html(article.source) if article.source else ''],
            ['Primary Topic', clean_html(article.primary_category_name)],
            ['Topics', clean_html(', '.join(article.categories))]
        ]
        
        # Create table with proper styling
        pub_table = Table(pub_details, colWidths=[first_col_width, second_col_width])
        pub_table.setStyle(details_table_style)
        elements.append(pub_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Summary section
        if article.summary:
            elements.append(Paragraph("Summary", heading_style))
            elements.append(Spacer(1, 0.2 * inch))
            extracted_summary, extracted_related_articles = extract_related_article(article.summary)
            elements.append(Paragraph(clean_html(extracted_summary), content_style))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Extended Excerpt section
        if article.extended_excerpt:
            elements.append(Paragraph("Extended Excerpt", heading_style))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(clean_html(article.extended_excerpt), content_style))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Related Articles section
        related_articles = None
        if extracted_related_articles:
            related_articles = keep_only_anchor_tags(extracted_related_articles)
        elif article.related_articles:
            related_articles = "\n".join([
                f"• <a href=\"{item['link']}\">{clean_html(item['title'])}</a>"
                for item in article.related_articles
            ])
        
        if related_articles:
            elements.append(Paragraph("Related Articles", heading_style))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(related_articles, content_style))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Metadata section
        elements.append(Paragraph("Additional Information", heading_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        metadata = []
        if article.article_link:
            metadata.append(f"Article URL: <a href=\"{article.article_link}\">{article.article_link}</a>")
        if article.permalink:
            metadata.append(f"Permalink: <a href=\"{article.permalink}\">{article.permalink}</a>")
        if article.pdf_file_url:
            metadata.append(f"PDF URL: <a href=\"{article.pdf_file_url}\">{article.pdf_file_url}</a>")
        if article.featured_image_url:
            metadata.append(f"Featured Image: <a href=\"{article.featured_image_url}\">{article.featured_image_url}</a>")
        
        for meta_item in metadata:
            elements.append(Paragraph(meta_item, italic_style))
            elements.append(Spacer(1, 0.1 * inch))
        
        # Build the PDF
        doc.build(elements)
        logger.info(f"Successfully generated PDF: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating PDF for article '{article.headline}': {str(e)}")
        return False

def convert_date_format(date_str: str) -> str:
    """Convert date string to desired format"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_str

def clean_html(text: str) -> str:
    """Clean HTML from text and normalize whitespace"""
    if not text:
        return ""
    soup = BeautifulSoup(text, 'html.parser')
    clean_text = soup.get_text(separator=' ')
    return ' '.join(clean_text.split())

def keep_only_anchor_tags(html: str) -> str:
    """Keep only anchor tags from HTML and clean up the rest"""
    if not html:
        return ""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(True):
        if tag.name != 'a':
            tag.unwrap()
    return str(soup)

def extract_related_article(text: str) -> tuple[str, Optional[str]]:
    """Extract related articles section from text if present"""
    if not text:
        return "", None
        
    # Split on "Related Articles:" if present
    parts = text.split("Related Articles:", 1)
    if len(parts) == 1:
        return text, None
        
    return parts[0].strip(), parts[1].strip()
