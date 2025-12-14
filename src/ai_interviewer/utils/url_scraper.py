"""
URL Scraper with SSRF Protection
Secure URL scraping with validation and content limits.
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional

from .input_validator import InputValidator
from .config import Config
from ..exceptions import ProcessingError, SecurityError, ResourceError
from .error_handler import ErrorHandler

logger = logging.getLogger(__name__)


class URLScraper:
    """
    Secure utility to extract readable text from Job Description URLs.
    
    Security Features:
    - SSRF protection via URL validation
    - Content length limits
    - Timeout protection
    - Request size limits
    """
    
    # Maximum response size (10MB)
    MAX_RESPONSE_SIZE = 10 * 1024 * 1024
    
    @staticmethod
    def extract_text(url: str) -> Optional[str]:
        """
        Fetches URL and extracts main text content with SSRF protection.
        
        Args:
            url: URL to scrape (must pass SSRF validation)
            
        Returns:
            Extracted text content (max Config.MAX_SCRAPED_CONTENT_LENGTH chars) or None on error
            
        Security:
        - Validates URL to prevent SSRF attacks
        - Enforces timeout and size limits
        - Sanitizes extracted content
        """
        # Validate URL first (SSRF protection)
        is_valid, error_msg = InputValidator.validate_url(url)
        if not is_valid:
            logger.warning(f"URL validation failed: {error_msg} for URL: {url[:50]}...")
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Make request with timeout and size limit
            # Note: requests.get doesn't support max_redirects parameter
            # Redirects are handled automatically with allow_redirects=True (default)
            response = requests.get(
                url, 
                headers=headers, 
                timeout=10,
                stream=True,  # Stream to check size
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check content length header
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > URLScraper.MAX_RESPONSE_SIZE:
                logger.warning(f"Response too large: {content_length} bytes")
                return None
            
            # Read content with size limit
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > URLScraper.MAX_RESPONSE_SIZE:
                    logger.warning(f"Response exceeded size limit during download")
                    return None
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements (XSS prevention)
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Enforce content length limit
            max_length = Config.MAX_SCRAPED_CONTENT_LENGTH
            if len(text) > max_length:
                logger.info(f"Content truncated from {len(text)} to {max_length} characters")
                text = text[:max_length]
            
            return text
            
        except requests.exceptions.Timeout:
            ErrorHandler.log_error(
                ResourceError("URL scraping timeout", resource_type="network", limit="10s"),
                {"operation": "extract_text", "url": url[:50]}
            )
            return None
        except requests.exceptions.RequestException as e:
            ErrorHandler.log_error(
                ProcessingError(f"Request error: {str(e)}", operation="extract_text"),
                {"operation": "extract_text", "url": url[:50]}
            )
            return None
        except Exception as e:
            ErrorHandler.log_error(
                ProcessingError(f"Unexpected error: {str(e)}", operation="extract_text"),
                {"operation": "extract_text", "url": url[:50]}
            )
            return None
