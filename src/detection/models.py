"""
src/detection/models.py
POCO/DTO - Structures de données pures avec validation Pydantic
"""

from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional


class ComplexityLevel(str, Enum):
    """Niveaux de complexité de traitement"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DocumentType(BaseModel):
    """Structure validée pour définir un type de document supporté"""

    extension: str = Field(..., description="Extension du fichier (ex: .docx)")
    mime_type: str = Field(..., description="type MIME officiel")
    description: str = Field(..., description="Description lisible du format")
    parser_module: str = Field(..., description="Module Python requis pour parser")
    complexity: ComplexityLevel = Field(..., description="Complexité de traitement")

    @field_validator("extension")
    @classmethod
    def extension_must_start_with_dot(cls, v):
        if not v.startswith("."):
            raise ValueError("Extension doit commencer par un point")
        return v.lower()

    @field_validator("mime_type")
    @classmethod
    def mime_type_must_be_valid(cls, v):
        """Valider le format du type MIME"""
        if "/" not in v:
            raise ValueError("Type MIME doit contenir un slash")
        return v


class FileInfo(BaseModel):
    """Informations de base d'un fichier"""

    path: str
    name: str
    stem: str  # retourne le nom du fichier sans l’extension
    extension: str
    size_bytes: int
    size_mb: float
    size_category: str


class DetectionResult(BaseModel):
    """Résultat de la détection type"""

    method: str
    detected_type: str
    mime_type: str
    description: str
    confidence: float
    is_supported: bool
    resolution: Optional[str] = None
    extension_match: Optional[bool] = None


class ProcessingInfo(BaseModel):
    "Informations de traitement"

    can_process: bool
    recommended_parser: Optional[str] = None
    complexity: Optional[str] = None
    estimated_time: Optional[str] = None
    memory_requirement: Optional[str] = None
    reason: Optional[str] = None


class DocumentDetectionResult(BaseModel):
    """Résultat complet de la détection"""

    file_info: Optional[FileInfo] = None
    detection: Optional[DetectionResult] = None
    processing: Optional[ProcessingInfo] = None
    status: str
    error: Optional[str] = None
