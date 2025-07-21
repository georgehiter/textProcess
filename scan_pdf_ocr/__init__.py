"""
扫描版PDF OCR识别模块
提供高质量的PDF文档OCR识别功能
"""

from .scan_pdf_ocr import extract_scan_pdf
from .scan_config import (
    CHINESE_OCR_BEST_PRACTICES,
    DEFAULT_CHINESE_OCR_CONFIG,
    DEFAULT_ENGLISH_OCR_CONFIG,
    SCAN_OCR_CONFIGS,
    LANGUAGE_DETECTION_CONFIG,
    LANGUAGE_OCR_CONFIGS,
)

try:
    from .document_analyzer import detect_document_type
except ImportError:
    detect_document_type = None

try:
    from .language_detector import detect_language
except ImportError:
    detect_language = None

__version__ = "1.0.0"
__author__ = "OCR Team"

__all__ = [
    "extract_scan_pdf",
    "detect_document_type",
    "detect_language",
    "CHINESE_OCR_BEST_PRACTICES",
    "DEFAULT_CHINESE_OCR_CONFIG",
    "DEFAULT_ENGLISH_OCR_CONFIG",
    "SCAN_OCR_CONFIGS",
    "LANGUAGE_DETECTION_CONFIG",
    "LANGUAGE_OCR_CONFIGS",
]
