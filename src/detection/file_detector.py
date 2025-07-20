"""
src/detection/file_detector.py
Étape 1.1 - Détection intelligente du type de document
Service pur utilisant DocumentService pour la logique métier
"""

import os
from pathlib import Path
import mimetypes

from .models import FileInfo, DetectionResult, ProcessingInfo, DocumentDetectionResult

from .document_service import DocumentService

# Import conditionnel pour la detection MIME avancée
try:
    import magic

    HAS_MAGIC = True
except ImportError:
    try:
        import filetype

        HAS_FILETYPE = True
        HAS_MAGIC = False
    except ImportError:
        HAS_MAGIC = False
        HAS_FILETYPE = False


class DocumentTypeDetector:
    """
    Détecteur intelligent de type de document
    Implémente l'étape 1.1 avec stratégie multi-niveau
    """

    def __init__(self, document_service: DocumentService = None):
        """Initialisation avec injection de dépendance"""
        self.document_service = document_service or DocumentService()

    def detect_document_type(self, file_path: str) -> DocumentDetectionResult:
        """Détection multi-niveau du type de document"""
        # Étape 1: Vérification d'existence
        path_obj = Path(file_path)
        if not path_obj.exists():
            return DocumentDetectionResult(
                status="error", error=f"Fichier non trouvé:{file_path}"
            )
        try:
            # Étape 2: Information de base
            file_info = self._extract_file_info(path_obj)

            # Étape 3: Détection par extension
            extension_detection = self._detect_by_extension(path_obj)

            # Étape 4: Détection par contenu (MIME)
            mime_detection = self._detect_by_mime(path_obj)

            # Étape 5: Validation et resolution des conflits
            final_detection = self._resolve_detection_conflicts(
                extension_detection, mime_detection
            )
            # Étape 6: Enrichissement avec métadonnées
            processing_info = self._generate_processing_info(final_detection, file_info)

            return DocumentDetectionResult(
                file_info=file_info,
                detection=final_detection,
                processing=processing_info,
                status="success",
            )

        except Exception as e:
            return DocumentDetectionResult(
                status="error", error=f"Erreur lors de l'analyse: {str(e)}"
            )

    def _extract_file_info(self, path_obj: Path) -> FileInfo:
        """Extraction des informations de base du fichier"""
        file_stats = path_obj.stat()
        size_bytes = file_stats.st_size
        size_mb = round(size_bytes / (1024 * 1024), 2)

        return FileInfo(
            path=str(path_obj.resolve(strict=False)),
            name=path_obj.name,
            stem=path_obj.stem,
            extension=path_obj.suffix.lower(),
            size_bytes=size_bytes,
            size_mb=size_mb,
            size_category=self._categorize_file_size(size_bytes),
        )

    def _detect_by_extension(self, path_obj: Path) -> DetectionResult:
        """Détection basée sur l'extension du fichier"""
        extension = path_obj.suffix.lower()

        # utilisation de DocumentService
        if self.document_service.is_supported(extension):
            doc_type = self.document_service.get_document_type(extension)
            return DetectionResult(
                method="extension",
                detected_type=extension,
                mime_type=doc_type.mime_type,
                description=doc_type.description,
                confidence=0.7,
                is_supported=True,
            )
        else:
            return DetectionResult(
                method="extension",
                detected_type=extension,
                mime_type="unknown",
                description="Type non supporté",
                confidence=0.3,
                is_supported=False,
            )

    def _detect_by_mime(self, path_obj: Path) -> DetectionResult:
        """Détection basée sur le contenu réel (MIME type)"""
        try:
            # Méthode 1: python-magic (plus précise)
            if HAS_MAGIC:
                mime_type = magic.from_file(str(path_obj), mime=True)
                confidence = 0.9

            # Méthode 2: filetype (alternative)
            elif HAS_FILETYPE:
                kind = filetype.guess(str(path_obj))
                mime_type = kind.mime if kind else None
                confidence = 0.8

            # Méthode 3: mimetypes (fallback)
            else:
                mime_type, _ = mimetypes.guess_type(str(path_obj))
                confidence = 0.6

            # Utilisation du DocumentService pour la résolution
            detected_ext = self.document_service.get_extension_from_mime(mime_type)

            if detected_ext:
                doc_type = self.document_service.get_document_type(detected_ext)
                return DetectionResult(
                    method="mime_content",
                    detected_type=detected_ext,
                    mime_type=mime_type,
                    description=doc_type.description,
                    confidence=confidence,
                    is_supported=True,
                )
            else:
                return DetectionResult(
                    method="mime_content",
                    detected_type="unknown",
                    mime_type=mime_type or "unknown",
                    description="Type non reconnu par type",
                    confidence=0.2,
                    is_supported=False,
                )
        except Exception as e:
            return DetectionResult(
                method="mime_content",
                detected_type="unknown",
                mime_type="error",
                description=f"Erreur détection MIME: {str(e)}",
                confidence=0.0,
                is_supported=False,
            )

    def _resolve_detection_conflicts(
        self, ext_detection: DetectionResult, mime_detection: DetectionResult
    ) -> DetectionResult:
        """Résolution des conflits entre détection par extension vs contenu"""
        # Si pas d'erreur dans la détection MIME et confiance élevée
        if mime_detection.confidence > 0.7 and mime_detection.mime_type != "error":
            # Vérification cohérence
            ext_type = ext_detection.detected_type
            mime_type = mime_detection.detected_type

            if ext_type == mime_type:
                # Parfaite Cohérence
                confidence = min(
                    1.0, ext_detection.confidence + mime_detection.confidence
                )
                resolution = "coherent"
            else:
                # Conflit détecté - privilegier le contenu
                confidence = mime_detection.confidence
                resolution = "mime_priority"

            result = mime_detection.model_copy()
            result.confidence = confidence
            result.resolution = resolution
            result.extension_match = ext_type == mime_type
        else:
            # Fallback sur l'extension
            result = ext_detection.model_copy()
            result.resolution = "extension_fallback"

        return result

    def _generate_processing_info(
        self, detection: DetectionResult, file_info: FileInfo
    ) -> ProcessingInfo:
        """Génération des infos de traitement"""
        detected_type = detection.detected_type
        is_supported = detection.is_supported

        if is_supported and self.document_service.is_supported(detected_type):
            doc_type = self.document_service.get_document_type(detected_type)

            # Estimation de la complexité basé sur la taille
            size_complexity = self._estimate_size_complexity(file_info.size_mb)
            overall_complexity = self._max_complexity(
                doc_type.complexity.value, size_complexity
            )

            return ProcessingInfo(
                can_process=True,
                recommended_parser=doc_type.parser_module,
                complexity=overall_complexity,
                estimated_time=self._estimate_processing_time(
                    overall_complexity, file_info.size_mb
                ),
                memory_requirement=self._estimate_memory_usage(
                    detected_type, file_info.size_mb
                ),
            )
        else:
            return ProcessingInfo(
                can_process=False, reason="Type de fichier non supporté"
            )

    # Méthodes utilitaires privées
    def _categorize_file_size(self, size_bytes: int) -> str:
        """Catégorisation de la taille du fichier"""
        size_mb = size_bytes / (1024 * 1024)
        if size_mb < 1:
            return "small"
        elif size_mb < 10:
            return "medium"
        elif size_mb < 50:
            return "large"
        else:
            return "very_large"

    def _estimate_size_complexity(self, size_mb: float) -> str:
        """Estimation de complexité basée sur la taille"""
        if size_mb < 5:
            return "low"
        elif size_mb < 20:
            return "medium"
        else:
            return "high"

    def _max_complexity(self, complexity1: str, complexity2: str) -> str:
        """Retourner la complexité maximale entre deux: type de document et taille de doc"""
        order = {"low": 1, "medium": 2, "high": 3}
        if order.get(complexity1, 0) >= order.get(complexity2, 0):
            return complexity1
        return complexity2

    def _estimate_processing_time(self, complexity: str, size_mb: float) -> str:
        """Estimation du temps de traitement"""
        base_times = {"low": 1, "medium": 5, "high": 15}  # secondes
        base_time = base_times.get(complexity, 10)

        # facteur taille
        size_factor = max(1, size_mb / 5)
        estimated_seconds = base_time * size_factor

        if estimated_seconds < 60:
            return f"~{int(estimated_seconds)}s"
        else:
            return f"~{int(estimated_seconds / 60)}min"

    def _estimate_memory_usage(self, file_type: str, size_mb: float) -> str:
        """Estimation de l'usage memoire"""
        # Facteur multiplicateur par type
        memory_factors = {
            ".txt": 2,  # Texte = peu de mémoire
            ".docx": 4,  # Structure XML = plus de mémoire
            ".pdf": 6,  # Rendu + extraction = beaucoup
            ".odt": 5,  # Similaire à DOCX
        }

        factor = memory_factors.get(file_type, 4)
        estimated_mb = size_mb * factor

        if estimated_mb < 100:
            return "low"
        elif estimated_mb < 500:
            return "medium"
        else:
            return "high"
