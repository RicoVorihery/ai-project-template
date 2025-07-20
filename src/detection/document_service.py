"""
src/detection/document_service.py
Service Layer - Logique métier pour la gestion des types de documents
"""

from typing import Dict, Optional
from .models import DocumentType
from .config import get_supported_types, get_mime_to_extension_mapping


class DocumentService:
    """
    Service pour la gestion des types de documents supportés
    Encapsule toute la logique métier liée aux documents
    """

    def __init__(self):
        """Initialisation avec la configuration par defaut"""
        self._supported_types = get_supported_types()
        self._mime_to_extension = get_mime_to_extension_mapping()

    @property
    def supported_types(self) -> Dict[str, DocumentType]:
        """Accès en lecture seule aux types supportés"""
        return self._supported_types.copy()

    @property
    def mime_to_extension(self) -> Dict[str, str]:
        """Accès en lecture seule au mapping MIME"""
        return self._mime_to_extension.copy()

    def is_supported(self, extension: str) -> bool:
        """Vérifier si une extension est supportée"""
        return extension.lower() in self._supported_types

    def get_document_type(self, extension: str) -> Optional[DocumentType]:
        """Récupérer les informations d'un type de document"""
        return self._supported_types.get(extension.lower())

    def get_extension_from_mime(self, mime_type: str) -> Optional[str]:
        """Récupérer l'extension correspondant à un type MIME"""
        return self._mime_to_extension.get(mime_type)

    def add_document_type(self, doc_type: DocumentType) -> None:
        """Ajouter un nouveau type de document (avec validation)"""
        self._supported_types[doc_type.extension] = doc_type
        self._mime_to_extension[doc_type.mime_type] = doc_type.extension

    def remove_document_type(self, extension: str) -> bool:
        """Supprimer un type de document"""
        extension = extension.lower()
        if extension in self._supported_types:
            doc_type = self._supported_types[extension]
            # suppression des deux mappings
            del self._supported_types[extension]
            del self._mime_to_extension[doc_type.mime_type]
            return True
        return False

    def get_supported_extensions(self) -> list[str]:
        """Liste des extensions supportés

        Returns:
            list[str]: Liste des extensions (ex: ['.docx','.pdf'])
        """
        return list(self._supported_types.keys())

    def get_supported_mime_types(self) -> list[str]:
        """Liste des types MIME supportés

        Returns:
            list[str]: Liste des types MIME
        """
        return list(self._mime_to_extension.keys())

    def export_config(self) -> Dict:
        """Exporter la configuration en dictionnaire"""
        return {
            "supported_types": {
                ext: doc_type.model_dump()
                for ext, doc_type in self._supported_types.items()
            }
        }
