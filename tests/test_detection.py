"""Test simple pour vérifier que tout fonctionne
Mode MVP/POC - Tests rapides sans framework
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


def tests_models():
    """Test des modèles Pydantic"""
    print("Test des models...")

    try:
        from src.detection.models import ComplexityLevel, DocumentType

        # Test création valide
        doc = DocumentType(
            extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            description="Test Document",
            parser_module="python-docx",
            complexity=ComplexityLevel.MEDIUM,
        )
        print(f"DocumentType créé:{doc.extension}")

        # Test validation extension
        try:
            bad_doc = DocumentType(
                extension="docx",  # Sans point - doit échouer
                mime_type="application/test",
                description="Bad",
                parser_module="test",
                complexity=ComplexityLevel.LOW,
            )
            print("Validation extension ratée")
        except Exception as e:
            print(f"Validation extension OK: {e}")

        # Test validation mime_type
        try:
            bad_doc = DocumentType(
                extension=".docx",  # Sans point - doit échouer
                mime_type="bad_mime_sans_slash",
                description="Bad",
                parser_module="test",
                complexity=ComplexityLevel.LOW,
            )
            print("Validation mime type ratée")
        except Exception as e:
            print(f"Validation mime type OK:{e}")

    except Exception as e:
        print(f"Erreur models: {e}")


def test_config():
    try:
        from src.detection.config import (
            get_supported_types,
            get_mime_to_extension_mapping,
            SUPPORTED_EXTENSIONS,
        )

        # Test données de base
        assert ".docx" in SUPPORTED_EXTENSIONS
        assert ".pdf" in SUPPORTED_EXTENSIONS
        print("Configuration de base OK")

        # Test get supported types
        types = get_supported_types()
        assert len(types) > 0
        assert ".docx" in types
        print(f"Factory OK - {len(types)} types créés")

        # Test get mime to extension mapping

        mimes_dic = get_mime_to_extension_mapping()

        assert len(mimes_dic) > 0
        assert "application/pdf" in mimes_dic

        print(f"Mimes types OK - {len(mimes_dic)} MIMES créés")

    except Exception as e:
        print(f"Erreur config: {e}")


def test_services():
    try:
        from src.detection.document_service import DocumentService

        service = DocumentService()

        # Test support
        assert service.is_supported(".docx")
        assert not service.is_supported(".xyz")
        print("Support detection OK")

        # Test récupération
        doc_type = service.get_document_type(".pdf")
        assert doc_type is not None
        assert doc_type.extension == ".pdf"

        print(f"Document Type:{doc_type}")
        print("Document type retrieval OK")

        # récupérer extension à partir de MIME
        extension = service.get_extension_from_mime("application/pdf")
        assert extension is not None and extension != ""
        print(f"Extension : {extension}")
        print("Extraction retrieval OK")

    except Exception as e:
        print(f"Erreur services: {e}")


def test_detector():
    """Test du détecteur avec fichier fictif"""
    print("\n Test du détecteur...")

    try:
        from src.detection.file_detector import DocumentTypeDetector

        detector = DocumentTypeDetector()

        # Test fichier inexistant
        result = detector.detect_document_type("fichier_inexistant.docx")
        assert result.status == "error"
        print("Gestion fichier inexistant OK")

        # Test avec fichier réel si disponible
        import os

        script_dir = Path(__file__).parent
        test_file = script_dir / "test_document.txt"

        if test_file.exists():
            result = detector.detect_document_type(str(test_file))
            print(f"Fichier réel testé: {result.status}")
            print(vars(result))
        else:
            print("Pas de fichier test disponible")

    except Exception as e:
        print(f"Erreur Détecteur: {e}")


def create_test_file():
    """Créer un fichier de test simple"""
    print("\n Créer fichier de test...")
    try:
        with open("tests/test_document.txt", "w", encoding="utf-8") as f:
            f.write(
                "Ceci est un document de test. \nLe système doit fonctionner correctement."
            )
        print("Fichier test_document.txt créé")
    except Exception as e:
        print(f" Erreur création fichier: {e}")


if __name__ == "__main__":
    print(" Tests simples POC")
    print("=" * 40)

    # Créer fichier de test
    create_test_file()

    # Test par couche
    tests_models()
    test_config()
    test_services()
    test_detector()
    print("\n🏁 Tests terminés!")
    print("Si tout est ✅, votre code fonctionne!")
