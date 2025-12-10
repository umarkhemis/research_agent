import requests
import PyPDF2
import io
from typing import Optional
import config
from utils.error_handler import logger, handle_errors, PDFProcessingError, ErrorContext
from agents.cache_manager import cache


class PDFAgent:
    """Handles PDF downloading and text extraction with robust error handling"""
    
    def __init__(self):
        self.timeout = config.PDF_TIMEOUT_SECONDS
        self.max_size = config.MAX_PDF_SIZE_MB * 1024 * 1024  # Convert to bytes
        logger.info("PDF Agent initialized")
    
    @handle_errors
    def download_pdf(self, pdf_url: str, paper_id: Optional[str] = None) -> Optional[bytes]:
        """
        Download PDF from URL with size limits and error handling
        
        Args:
            pdf_url: URL of the PDF
            paper_id: Optional paper ID for caching
            
        Returns:
            PDF content as bytes or None if failed
        """
        # Check cache first
        if paper_id:
            cached_pdf = cache.get_paper_cache(paper_id, "pdf_bytes")
            if cached_pdf:
                logger.debug(f"Using cached PDF for {paper_id}")
                return cached_pdf
        
        with ErrorContext("PDF Download", paper_id):
            try:
                # Stream the download to check size before loading all
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': pdf_url,  
                }
                
                response = requests.get(
                    pdf_url, 
                    stream=True, 
                    timeout=self.timeout,
                    headers=headers,
                    allow_redirects=True 
                )
                response.raise_for_status()
                
                
                # Check content length
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.max_size:
                    logger.warning(f"PDF too large: {int(content_length) / 1024 / 1024:.2f}MB")
                    raise PDFProcessingError(f"PDF exceeds maximum size of {config.MAX_PDF_SIZE_MB}MB")
                
                # Download in chunks
                pdf_bytes = b""
                for chunk in response.iter_content(chunk_size=8192):
                    pdf_bytes += chunk
                    if len(pdf_bytes) > self.max_size:
                        logger.warning("PDF exceeded size limit during download")
                        raise PDFProcessingError(f"PDF exceeds maximum size of {config.MAX_PDF_SIZE_MB}MB")
                
                logger.info(f"Downloaded PDF: {len(pdf_bytes) / 1024:.2f}KB")
                
                # Cache the PDF bytes
                if paper_id:
                    cache.set_paper_cache(paper_id, "pdf_bytes", pdf_bytes)
                
                return pdf_bytes
                
            except requests.exceptions.Timeout:
                logger.error(f"PDF download timed out: {pdf_url}")
                raise PDFProcessingError("PDF download timed out")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download PDF: {str(e)}")
                raise PDFProcessingError(f"Failed to download PDF: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error downloading PDF: {str(e)}")
                raise PDFProcessingError(f"Unexpected error: {str(e)}")
    
    @handle_errors
    def extract_text(self, pdf_bytes: bytes, paper_id: Optional[str] = None) -> Optional[str]:
        """
        Extract text from PDF bytes
        
        Args:
            pdf_bytes: PDF content as bytes
            paper_id: Optional paper ID for caching
            
        Returns:
            Extracted text or None if failed
        """
        # Check cache first
        if paper_id:
            cached_text = cache.get_paper_cache(paper_id, "pdf_text")
            if cached_text:
                logger.debug(f"Using cached PDF text for {paper_id}")
                return cached_text
        
        with ErrorContext("PDF Text Extraction", paper_id):
            try:
                reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                
                # Check if PDF is encrypted
                if reader.is_encrypted:
                    logger.warning("PDF is encrypted, attempting to decrypt")
                    try:
                        reader.decrypt("")
                    except:
                        raise PDFProcessingError("PDF is password-protected")
                
                # Extract text from all pages
                text_parts = []
                page_count = len(reader.pages)
                
                logger.debug(f"Extracting text from {page_count} pages")
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {str(e)}")
                        continue
                
                if not text_parts:
                    logger.warning("No text extracted from PDF")
                    raise PDFProcessingError("Could not extract text from PDF (might be image-based)")
                
                full_text = "\n\n".join(text_parts)
                
                # Clean up the text
                full_text = self._clean_text(full_text)
                
                logger.info(f"Extracted {len(full_text)} characters from PDF")
                
                # Cache the extracted text
                if paper_id:
                    cache.set_paper_cache(paper_id, "pdf_text", full_text)
                
                return full_text
                
            except PyPDF2.errors.PdfReadError as e:
                logger.error(f"PyPDF2 read error: {str(e)}")
                raise PDFProcessingError(f"Could not read PDF: {str(e)}")
            
            except Exception as e:
                logger.error(f"Text extraction failed: {str(e)}")
                raise PDFProcessingError(f"Text extraction failed: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace("\x00", "")
        text = text.replace("\uf0b7", "")  # Bullet points
        
        return text
    
    def process_pdf(self, pdf_url: str, paper_id: Optional[str] = None) -> Optional[str]:
        """
        Download and extract text from PDF in one operation
        
        Args:
            pdf_url: URL of the PDF
            paper_id: Optional paper ID for caching
            
        Returns:
            Extracted text or None if failed
        """
        try:
            # Download PDF
            pdf_bytes = self.download_pdf(pdf_url, paper_id)
            if not pdf_bytes:
                return None
            
            # Extract text
            text = self.extract_text(pdf_bytes, paper_id)
            return text
            
        except PDFProcessingError as e:
            logger.warning(f"PDF processing failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in PDF processing: {str(e)}")
            return None


# Global PDF agent instance
pdf_agent = PDFAgent()
