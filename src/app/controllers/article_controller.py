from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Generator
import os
import gc
import logging
import shutil
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.schema import Document, TextNode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from create_llama.backend.app.engine.loaders.file import FileLoaderConfig, get_file_documents
from create_llama.backend.app.engine.vectordb import get_vector_store
from src.utils.logger import get_logger
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from llama_index.core.settings import Settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Spacer, TableStyle, BaseDocTemplate, PageTemplate, Frame, KeepTogether, Table
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd

load_dotenv()

logger = get_logger()

# Constants for memory management
CHUNK_SIZE = Settings.chunk_size      # Default chunk size for text splitting
CHUNK_OVERLAP = Settings.chunk_overlap     # Default chunk overlap
GC_THRESHOLD = 5000  # New constant for garbage collection threshold

project_root = Path(__file__).parent.parent.parent.parent
# Constants for directories
STORAGE_DIR = os.path.join(project_root, 'storage')
ASSETS_DIR = os.path.join(project_root, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
LOGOS_DIR = ASSETS_DIR
STORAGE_PDFS_DIR = os.path.join(project_root, 'data', 'macro roundup')

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

title_style = ParagraphStyle('Title', fontSize=20, fontName='Arial-Bold', spaceAfter=12, alignment=1, textColor=colors.black)
heading_style = ParagraphStyle('Heading', fontSize=18, fontName='Arial-Bold', spaceAfter=12, textColor=colors.black)
subheading_style = ParagraphStyle('Subheading', fontSize=14, fontName='Arial-Bold', spaceAfter=6, textColor=HexColor('#1A76BD'))
tweet_style = ParagraphStyle('Subheading', fontSize=14, fontName='Arial', leading=12, spaceAfter=6, textColor=HexColor('#DA0000'))
normal_style = ParagraphStyle('Normal', fontSize=12, fontName='Arial', leading=12, spaceAfter=6)
all_subheading_style = ParagraphStyle('Heading', fontSize=14, fontName='Arial-Bold', spaceAfter=12, textColor=colors.black)
italic_style = ParagraphStyle('Italic', fontSize=12, fontName='Arial-Italic', leading=12, spaceAfter=6, textColor=colors.darkslategray)
content_style = ParagraphStyle('Content', fontSize=11, fontName='Arial', leading=14, spaceAfter=10)

def add_header(canvas, doc):
    canvas.saveState()
    
    # Define image paths
    logo_path = os.path.join(LOGOS_DIR, 'edward-conard-logo.png')
    badge_path = os.path.join(LOGOS_DIR, 'top-ten-nyt-best-seller-badge.png')
    
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

# API Security
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    logger.warning("API_TOKEN not set in environment variables. Webhook endpoints will be unavailable.")

api_key_header = APIKeyHeader(name="x-api-token", auto_error=False)

async def verify_token(api_key: str = Security(api_key_header)):
    if not API_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="API token authentication is not configured"
        )
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API token"
        )
    if api_key != API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid API token"
        )
    return api_key

router = APIRouter()

@router.post("/upload", response_model=ArticleUploadResponse, dependencies=[Depends(verify_token)])
async def upload_articles(articles: List[Article]):
    """
    Upload and process multiple articles. Protected by x-api-token header.
    """
    try:
        vector_store = get_vector_store()
        if not vector_store:
            raise HTTPException(status_code=500, detail="Failed to initialize vector store")
            
        processed_count = 0
        error_count = 0
        pdf_paths = []
        
        for article in articles:
            try:
                if process_article(article, vector_store):
                    processed_count += 1
                    pdf_path = os.path.join(
                        STORAGE_PDFS_DIR,
                        clean_filename(article.headline),
                        f"{clean_filename(article.headline)}.pdf"
                    )
                    pdf_paths.append(pdf_path)
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Error processing article {article.headline}: {str(e)}")
                error_count += 1
                continue
                
        return ArticleUploadResponse(
            message=f"Processed {processed_count} articles with {error_count} errors",
            processed_count=processed_count,
            error_count=error_count,
            pdf_paths=pdf_paths
        )
        
    except Exception as e:
        logger.error(f"Error in upload_articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        elements = []
        # Create the PDF
        
        doc = BaseDocTemplate(output_path, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                            leftMargin=0.5 * inch, rightMargin=0.5 * inch)

        frame = Frame(0.5 * inch, 0.5 * inch, doc.width, doc.height, id='normal')
        template = PageTemplate(id='macro_roundup', frames=frame, onPage=add_header)
        doc.addPageTemplates([template])

        elements.append(Spacer(1, 24))
        elements.append(Paragraph(f"Macro Roundup Article", heading_style))
        elements.append(Spacer(1, 12))

        # Headline and summary
        elements.append(Paragraph(f"<font color='black'>Headline:&nbsp;&nbsp;</font> {str(article.headline)}", subheading_style))
        elements.append(Spacer(1, 12))

        
        # Links
        if pd.notna(article.article_link):
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Article Link:</font></b>"
                                f"&nbsp;&nbsp;"
                                f"<u><font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{article.article_link}\">{article.article_link}</a></font></u>", normal_style))
            elements.append(Spacer(1, 12))
        
        # Publication details
        pub_details = [
            ['Author(s)', article.authors],
            ['Publication', article.publication],
            ['Publication Date', convert_date_format(str(article.publication_date).split(" ")[0])],
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
        tweet_texts = str(article.tweet)
        elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Tweet:</font></b>" 
                                f"&nbsp;&nbsp;"
                                f"<font name='{tweet_style.fontName}' size='{tweet_style.fontSize}' color='{tweet_style.textColor}'>{tweet_texts}</font>", tweet_style))
        elements.append(Spacer(1, 12))

        # Article Summary
        extrated_summary, extracted_related_articles = extract_related_article(article.summary)
        summary = clean_html(str(extrated_summary))
        elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Summary:</font></b>"
                                f"&nbsp;&nbsp;"
                                f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{summary}</font>", normal_style))
        elements.append(Spacer(1, 12))

        related_article_data = extracted_related_articles if extracted_related_articles != None else " ".join([f"<a href={related_article['link']}>{related_article['title']}</a>" for related_article in article.related_articles])
        # Related Articles
        if pd.notna(related_article_data) and related_article_data.strip():
            related_articles = keep_only_anchor_tags(related_article_data)
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Related Articles:</font></b>"
                                f"&nbsp;&nbsp;"
                        f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{related_articles}</font>", normal_style))
            
            elements.append(Spacer(1, 12))

        # Topics
        if pd.notna(article.primary_category_name):
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Primary Topic:</font></b>"
                                f"&nbsp;&nbsp;"
                        f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{article.primary_category_name}</font>", normal_style))
            elements.append(Spacer(1, 12))

        if len(article.categories) > 0:
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Topics:</font></b>"
                                f"&nbsp;&nbsp;"
                                    f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'>{','.join(article.categories)}</font>", normal_style))
            elements.append(Spacer(1, 12))

        if pd.notna(article.pdf_file_url):
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>PDF File URL:</font></b>"
                                f"&nbsp;&nbsp;"
                                    f"<u><font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{article.pdf_file_url}\">'{article.pdf_file_url}</a></font></u>", normal_style))
            elements.append(Spacer(1, 12))

        # Links
        if pd.notna(article.permalink):
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Permalink:</font></b>"
                                f"&nbsp;&nbsp;"
                                f"<u><font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{article.permalink}\">{article.permalink}</a></font></u>", normal_style))
            elements.append(Spacer(1, 12))

        if pd.notna(article.featured_image_url):
            # Featured Image
            elements.append(Paragraph(f"<b><font name='{all_subheading_style.fontName}' size='{all_subheading_style.fontSize}' color='{all_subheading_style.textColor}'>Featured Image Link:</font></b>"
                                f"&nbsp;&nbsp;"
                        f"<font name='{normal_style.fontName}' size='{normal_style.fontSize}' color='{normal_style.textColor}'><a href=\"{article.featured_image_url}\">{article.featured_image_url}</a></font>", normal_style))
            elements.append(Spacer(1, 12))

        # Build the PDF
        doc.build(elements)
        # i = i + 1

        get_logger().info(f"PDF created successfully: {output_path}")
        return True
        
    except Exception as e:
        get_logger().error(f"Error generating PDF for article '{article.headline}': {str(e)}")
        return False

def process_article(article: Article, vector_store) -> bool:
    """Process a single article and add it to the vector store with memory-efficient pipeline"""
    try:
        # Generate PDF
        data_dir = os.path.join(STORAGE_PDFS_DIR, clean_filename(article.headline))
        os.makedirs(data_dir, exist_ok=True)
        pdf_path = os.path.join(data_dir, f"{clean_filename(article.headline)}.pdf")
        
        if not generate_pdf(article, pdf_path):
            logger.error("Failed to generate PDF")
            return False
            
        logger.info(f"Generated PDF for article: {article.headline}")
        
        try:
            # Create document store
            from llama_index.core.storage.docstore import SimpleDocumentStore
            docstore = SimpleDocumentStore()
            
            # Load PDF content
            file_config = FileLoaderConfig(data_dir=data_dir)  # Fixed: Pass as keyword argument
            documents = get_file_documents(file_config)
            
            if not documents:
                logger.warning("No documents found for article")
                return False
            
            # Create ingestion pipeline
            pipeline = IngestionPipeline(
                transformations=[
                    SentenceSplitter(
                        chunk_size=Settings.chunk_size,
                        chunk_overlap=Settings.chunk_overlap,
                    ),
                    Settings.embed_model,
                ],
                docstore=docstore,
                docstore_strategy="upserts",
                vector_store=vector_store,
            )
            
            # Process documents in batches
            all_nodes = []
            node_count = 0
            batch_size = 1000  # MAX_BATCH_SIZE from memory requirements
            
            for i in range(0, len(documents), batch_size):
                doc_batch = documents[i:i + batch_size]
                try:
                    logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
                    batch_nodes = pipeline.run(show_progress=True, documents=doc_batch)
                    all_nodes.extend(batch_nodes)
                    node_count += len(batch_nodes)
                    
                    # Periodic storage persistence and cleanup
                    if node_count >= GC_THRESHOLD:
                        gc.collect()
                        logger.info(f"Memory cleanup - Processed {node_count} nodes")
                        node_count = 0
                except Exception as e:
                    logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
                    continue
            
            if all_nodes:
                logger.info(f"Successfully processed article with {len(all_nodes)} nodes")
                return True
            else:
                logger.error("No nodes generated from article")
                return False
                
        except Exception as e:
            logger.error(f"Error in document processing pipeline: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing article: {str(e)}")
        return False

def clean_html(html_str: str) -> str:
    """Clean HTML string"""
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text()

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

def cleanup_storage():
    """Clean up vector store collections"""
    try:
        logger.info("Starting storage cleanup...")
        
        # Clean up Qdrant collections
        vector_store = get_vector_store()
        
        try:
            # Delete collection with proper cleanup
            vector_store.delete_collection()
            logger.info("Deleted vector store collection")
            
            # Reset collection initialization flag
            vector_store._collection_initialized = False
            
            # Re-initialize collection with proper config
            if ensure_vector_store_collection(vector_store):
                logger.info("Re-initialized vector store collection")
            else:
                logger.warning("Failed to re-initialize vector store collection")
                
        except Exception as e:
            logger.error(f"Error cleaning up vector store: {str(e)}")
            return False
        
        # Clean up storage directories
        try:
            shutil.rmtree(STORAGE_PDFS_DIR)
            logger.info("Cleaned up PDF storage directory")
        except Exception as e:
            logger.warning(f"Error cleaning up PDF directory: {str(e)}")
        
        # Ensure storage directories exist
        ensure_directories()
        logger.info("Re-created storage directories")
        
        # Force garbage collection
        gc.collect()
        logger.info("Performed final garbage collection")
        
        return True
    except Exception as e:
        logger.error(f"Error during storage cleanup: {str(e)}")
        return False

@router.post("/reset")
async def reset_storage():
    """Reset vector store collections"""
    try:
        if cleanup_storage():
            return {"message": "Successfully reset vector store and cleaned up storage"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset vector store")
    except Exception as e:
        logger.error(f"Error in reset_storage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
