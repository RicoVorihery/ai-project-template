"""
src/detection/config.py
Configuration pure - Données statiques des types de documents supportés
"""

from typing import Dict
from .models import DocumentType, ComplexityLevel

# Configuration statique des types supportés
SUPPORTED_EXTENSIONS = {
    ".docx": {
        "extension": ".docx",
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "description": "Microsoft Word Document",
        "parser_module": "python-docx",
        "complexity": ComplexityLevel.MEDIUM,
    },
    ".pdf": {
        "extension": ".pdf",
        "mime_type": "application/pdf",
        "description": "PDF Document",
        "parser_module": "pdfplumber",
        "complexity": ComplexityLevel.HIGH,
    },
    ".txt": {
        "extension": ".txt",
        "mime_type": "text/plain",
        "description": "Plain Text File",
        "parser_module": "built-in",
        "complexity": ComplexityLevel.LOW,
    },
    ".odt": {
        "extension": ".odt",
        "mime_type": "application/vnd.oasis.opendocument.text",
        "description": "OpenDocument Text",
        "parser_module": "odfpy",
        "complexity": ComplexityLevel.MEDIUM,
    },
}


def get_supported_types() -> Dict[str, DocumentType]:
    """
    Factory function pour créer les DocumentType depuis la configuration
    Returns:
        Dict[str, DocumentType]: Mapping extension -> DocumentType validé
    """
    return {ext: DocumentType(**config) for ext, config in SUPPORTED_EXTENSIONS.items()}


def get_mime_to_extension_mapping() -> Dict[str, str]:
    """
    Créer le mapping MIME type -> extension depuis la configuration
    Returns:
        Dict[str, str]: Mapping MIME type -> extension
    """
    return {config["mime_type"]: ext for ext, config in SUPPORTED_EXTENSIONS.items()}
