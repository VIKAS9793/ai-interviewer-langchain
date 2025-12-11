import magic
import zipfile
import re
import os
import logging
from typing import Tuple, BinaryIO

logger = logging.getLogger(__name__)

class SecurityScanner:
    """
    Pre-ingestion security scanner for file uploads.
    Enforces strict validation of file types and content to prevent malicious ingestion.
    """
    
    # 10MB Limit (10 * 1024 * 1024 bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Allowed Magic MIME types
    ALLOWED_MIMES = {
        'application/pdf': '.pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
    }
    
    # PDF Threat Signatures
    PDF_THREATS = [
        rb'/JavaScript',
        rb'/JS',
        rb'/OpenAction',
        rb'/AA',  # Auto-Action
        rb'/Launch',
        rb'/RichMedia'
    ]

    @classmethod
    def scan_file(cls, file_obj, filename: str) -> Tuple[bool, str]:
        """
        Scans a file for security threats.
        Returns: (is_safe, refusal_reason)
        """
        try:
            # 1. Size Check
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(0)
            
            if size > cls.MAX_FILE_SIZE:
                 return False, f"File exceeds 10MB limit (Size: {size/1024/1024:.2f}MB)"
            
            if size == 0:
                return False, "File is empty"

            # 2. Magic Byte Validation (MIME Type)
            # Read first 2KB for magic check
            header = file_obj.read(2048)
            file_obj.seek(0)
            
            mime_type = magic.from_buffer(header, mime=True)
            
            if mime_type not in cls.ALLOWED_MIMES:
                return False, f"Invalid file type detected: {mime_type}. Only PDF and DOCX are allowed."
            
            # Extension vs MIME check
            expected_ext = cls.ALLOWED_MIMES[mime_type]
            if not filename.lower().endswith(expected_ext):
                return False, f"Extension mismatch. Detected {mime_type} but filename is {filename}"

            # 3. Deep Content Scanning
            if mime_type == 'application/pdf':
                return cls._scan_pdf(file_obj)
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return cls._scan_docx(file_obj)
                
            return True, "Safe"
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return False, "Security scan error"

    @classmethod
    def _scan_pdf(cls, file_obj) -> Tuple[bool, str]:
        """Deep scan for malicious PDF content"""
        content = file_obj.read()
        file_obj.seek(0)  # Reset pointer
        
        for threat in cls.PDF_THREATS:
            if threat in content:
                # Determine threat name for log
                threat_name = threat.decode('utf-8')
                return False, f"Malicious content detected: PDF contains executable code ({threat_name})"
        
        return True, "Safe"

    @classmethod
    def _scan_docx(cls, file_obj) -> Tuple[bool, str]:
        """Deep scan for malicious DOCX content (Macros, OLE)"""
        try:
            if not zipfile.is_zipfile(file_obj):
                return False, "Invalid DOCX format"
                
            with zipfile.ZipFile(file_obj) as zf:
                file_list = zf.namelist()
                
                # Check for Macros
                for f in file_list:
                    if f.startswith('word/vba') or f.endswith('.bin'):
                         return False, "Malicious content detected: DOCX contains Macros (VBA)"
                    
                    if 'oleObject' in f:
                        return False, "Malicious content detected: DOCX contains OLE Objects"
                        
            file_obj.seek(0)
            return True, "Safe"
            
        except Exception as e:
            return False, f"DOCX scan failed: {str(e)}"
