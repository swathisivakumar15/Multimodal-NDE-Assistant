import os
import hashlib
import magic
import logging
import uuid
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from app import app, db
from models import UploadedFile

ALLOWED_EXTENSIONS = {
    'pdf': ['application/pdf'],
    'image': ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'],
    'audio': ['audio/wav', 'audio/mp3', 'audio/m4a', 'audio/ogg']
}

def get_file_hash(file_path):
    """Generate SHA-256 hash of a file for corruption detection"""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Error generating file hash: {str(e)}")
        return None

def validate_file_safety(file_path, expected_type=None):
    """
    Validate file safety and detect corruption.
    Returns dict with validation results.
    """
    try:
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            return {
                'is_safe': False,
                'is_corrupted': True,
                'error': 'File does not exist or is not accessible.'
            }
        
        # Check file size (must be > 0)
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return {
                'is_safe': False,
                'is_corrupted': True,
                'error': 'File is empty or corrupted.'
            }
        
        # Detect actual file type using python-magic
        try:
            mime_type = magic.from_file(file_path, mime=True)
        except Exception as e:
            logging.error(f"Magic file type detection error: {str(e)}")
            return {
                'is_safe': False,
                'is_corrupted': True,
                'error': 'Unable to determine file type. File may be corrupted.'
            }
        
        # Validate against expected type
        is_allowed = False
        file_category = None
        
        for category, allowed_types in ALLOWED_EXTENSIONS.items():
            if mime_type in allowed_types:
                is_allowed = True
                file_category = category
                break
        
        if not is_allowed:
            return {
                'is_safe': False,
                'is_corrupted': False,
                'error': f'File type {mime_type} is not allowed. Please upload PDF, image, or audio files only.'
            }
        
        # Additional validation based on file type
        if file_category == 'pdf':
            pdf_validation = validate_pdf_integrity(file_path)
            if not pdf_validation['is_valid']:
                return {
                    'is_safe': False,
                    'is_corrupted': pdf_validation['is_corrupted'],
                    'error': pdf_validation['error']
                }
        
        elif file_category == 'image':
            image_validation = validate_image_integrity(file_path)
            if not image_validation['is_valid']:
                return {
                    'is_safe': False,
                    'is_corrupted': image_validation['is_corrupted'],
                    'error': image_validation['error']
                }
        
        return {
            'is_safe': True,
            'is_corrupted': False,
            'mime_type': mime_type,
            'file_category': file_category,
            'file_size': file_size
        }
        
    except Exception as e:
        logging.error(f"File safety validation error: {str(e)}")
        return {
            'is_safe': False,
            'is_corrupted': True,
            'error': f'Unexpected error during file validation: {str(e)}'
        }

def validate_pdf_integrity(file_path):
    """Validate PDF file integrity and readability"""
    try:
        # Try with PyMuPDF first (more robust)
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return {
                    'is_valid': False,
                    'is_corrupted': True,
                    'error': 'PDF file appears to be empty or corrupted.'
                }
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as pdf_file:
                    reader = PdfReader(pdf_file)
                    page_count = len(reader.pages)
                    
                    if page_count == 0:
                        return {
                            'is_valid': False,
                            'is_corrupted': True,
                            'error': 'PDF file appears to be empty or corrupted.'
                        }
            except Exception as e2:
                return {
                    'is_valid': False,
                    'is_corrupted': True,
                    'error': 'PDF file is corrupted and cannot be processed.'
                }
        
        return {
            'is_valid': True,
            'is_corrupted': False,
            'page_count': page_count
        }
        
    except Exception as e:
        logging.error(f"PDF validation error: {str(e)}")
        return {
            'is_valid': False,
            'is_corrupted': True,
            'error': f'Error validating PDF: {str(e)}'
        }

def validate_image_integrity(file_path):
    """Validate image file integrity"""
    try:
        from PIL import Image
        
        try:
            with Image.open(file_path) as img:
                # Try to load the image data
                img.verify()
                
                # Check basic properties
                if img.size[0] == 0 or img.size[1] == 0:
                    return {
                        'is_valid': False,
                        'is_corrupted': True,
                        'error': 'Image has invalid dimensions.'
                    }
        except Exception as e:
            return {
                'is_valid': False,
                'is_corrupted': True,
                'error': 'Image file is corrupted or in an unsupported format.'
            }
        
        return {
            'is_valid': True,
            'is_corrupted': False
        }
        
    except ImportError:
        # PIL not available, skip detailed image validation
        logging.warning("PIL not available for image validation")
        return {
            'is_valid': True,
            'is_corrupted': False
        }
    except Exception as e:
        logging.error(f"Image validation error: {str(e)}")
        return {
            'is_valid': False,
            'is_corrupted': True,
            'error': f'Error validating image: {str(e)}'
        }

def handle_file_upload(file, session_id):
    """
    Handle file upload with safety checks and corruption detection.
    Returns dict with upload results.
    """
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            return {
                'status': 'error',
                'error': 'Invalid filename provided.'
            }
        
        # Generate unique filename to prevent conflicts
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file temporarily
        file.save(file_path)
        
        # Validate file safety
        validation_result = validate_file_safety(file_path)
        
        if not validation_result['is_safe']:
            # Remove unsafe file
            try:
                os.remove(file_path)
            except:
                pass
            
            return {
                'status': 'error',
                'error': validation_result['error'],
                'is_corrupted': validation_result['is_corrupted']
            }
        
        # Generate file hash
        file_hash = get_file_hash(file_path)
        
        # Save file information to database
        uploaded_file = UploadedFile()
        uploaded_file.filename = filename
        uploaded_file.file_path = file_path
        uploaded_file.file_type = validation_result['mime_type']
        uploaded_file.file_size = validation_result['file_size']
        uploaded_file.file_hash = file_hash or 'unknown'
        uploaded_file.session_id = session_id
        uploaded_file.is_corrupted = validation_result['is_corrupted']
        
        db.session.add(uploaded_file)
        db.session.commit()
        
        return {
            'status': 'success',
            'filename': filename,
            'file_path': file_path,
            'file_type': validation_result['mime_type'],
            'file_size': validation_result['file_size'],
            'file_category': validation_result['file_category']
        }
        
    except Exception as e:
        # Clean up file if something went wrong
        try:
            if locals().get('file_path') and os.path.exists(locals().get('file_path', '')):
                os.remove(locals().get('file_path', ''))
        except:
            pass
        
        logging.error(f"File upload error: {str(e)}")
        return {
            'status': 'error',
            'error': f'Failed to process file upload: {str(e)}'
        }

def extract_pdf_text(file_path):
    """Extract text content from PDF files"""
    try:
        text_content = ""
        
        # Try PyMuPDF first (better for complex PDFs)
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            doc.close()
        except Exception as e:
            # Fallback to PyPDF2
            logging.warning(f"PyMuPDF failed, trying PyPDF2: {str(e)}")
            try:
                with open(file_path, 'rb') as pdf_file:
                    reader = PdfReader(pdf_file)
                    for page in reader.pages:
                        text_content += page.extract_text()
            except Exception as e2:
                logging.error(f"PDF text extraction failed: {str(e2)}")
                return None
        
        # Clean up extracted text
        text_content = text_content.strip()
        
        if len(text_content) < 50:
            return None  # Likely an image-based PDF or extraction failed
        
        return text_content
        
    except Exception as e:
        logging.error(f"PDF text extraction error: {str(e)}")
        return None

def cleanup_old_files(max_age_hours=24):
    """Clean up old uploaded files to save disk space"""
    try:
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        old_files = UploadedFile.query.filter(
            UploadedFile.created_at < cutoff_time
        ).all()
        
        for file_record in old_files:
            try:
                # Remove physical file
                if os.path.exists(file_record.file_path):
                    os.remove(file_record.file_path)
                
                # Remove database record
                db.session.delete(file_record)
            except Exception as e:
                logging.error(f"Error cleaning up file {file_record.filename}: {str(e)}")
        
        db.session.commit()
        logging.info(f"Cleaned up {len(old_files)} old files")
        
    except Exception as e:
        logging.error(f"File cleanup error: {str(e)}")
