"""
语言检测模块
用于智能检测文档语言类型，优化OCR配置选择
"""

import re
from typing import Tuple, List, Dict, Any
from langdetect import detect, detect_langs, LangDetectException

# 导入配置文件
from .scan_config import (
    LANGUAGE_DETECTION_CONFIG,
    LANGUAGE_OCR_CONFIGS,
    SCAN_OCR_CONFIGS,
)


def detect_language(text: str) -> Tuple[str, float]:
    """
    检测文本的主要语言类型（增强版）

    Args:
        text: 待检测的文本

    Returns:
        Tuple[str, float]: (语言代码, 置信度)
    """
    if (
        not text
        or len(text.strip())
        < LANGUAGE_DETECTION_CONFIG["min_text_length_for_detection"]
    ):
        return "unknown", 0.0

    try:
        # 1. 字符统计验证
        char_distribution = analyze_language_distribution(text)

        # 2. 如果中文字符比例很高，直接返回中文
        if char_distribution.get("chinese", 0) > 0.6:
            return "zh", 0.9

        # 3. 如果英文字符比例很高，直接返回英文
        if char_distribution.get("english", 0) > 0.6:
            return "en", 0.9

        # 4. 使用langdetect进行检测
        main_lang = detect(text)

        # 5. 获取所有语言的置信度
        lang_probs = detect_langs(text)

        # 6. 找到主要语言的置信度
        confidence = 0.0
        for lang_prob in lang_probs:
            if lang_prob.lang == main_lang:
                confidence = lang_prob.prob
                break

        # 7. 语言代码映射
        lang_mapping = {
            "zh": "zh",  # 中文
            "zh-cn": "zh",
            "zh-tw": "zh",
            "zh-hk": "zh",
            "en": "en",  # 英文
            "ja": "ja",  # 日文
            "ko": "ko",  # 韩文
        }

        detected_lang = lang_mapping.get(main_lang, main_lang)

        # 8. 特殊处理：如果检测为韩文但中文字符比例较高，重新判断
        if detected_lang == "ko" and char_distribution.get("chinese", 0) > 0.3:
            # 可能是中文被误判为韩文
            if confidence < 0.8:  # 置信度不够高时
                return "zh", 0.7

        # 9. 如果检测为中文但置信度较低，进行二次验证
        if detected_lang == "zh" and confidence < 0.6:
            # 检查是否真的是中文
            if char_distribution.get("chinese", 0) < 0.3:
                return "unknown", confidence

        return detected_lang, confidence

    except LangDetectException:
        return "unknown", 0.0


def detect_mixed_language(text: str) -> Tuple[str, float]:
    """
    检测混合语言文档

    Args:
        text: 待检测的文本

    Returns:
        Tuple[str, float]: (语言类型, 置信度)
    """
    if (
        not text
        or len(text.strip())
        < LANGUAGE_DETECTION_CONFIG["min_text_length_for_detection"]
    ):
        return "unknown", 0.0

    try:
        # 获取所有语言的置信度
        lang_probs = detect_langs(text)

        if len(lang_probs) == 0:
            return "unknown", 0.0

        # 检查是否有多种语言
        if len(lang_probs) > 1:
            # 检查中英文混合
            zh_prob = 0.0
            en_prob = 0.0

            for lang_prob in lang_probs:
                if lang_prob.lang in ["zh", "zh-cn", "zh-tw", "zh-hk"]:
                    zh_prob += lang_prob.prob
                elif lang_prob.lang == "en":
                    en_prob += lang_prob.prob

            # 如果中英文都有一定比例，认为是混合语言
            if zh_prob > 0.2 and en_prob > 0.2:
                return "mixed", max(zh_prob, en_prob)

        # 单一语言，返回主要语言
        main_lang = lang_probs[0].lang
        confidence = lang_probs[0].prob

        lang_mapping = {
            "zh": "zh",
            "zh-cn": "zh",
            "zh-tw": "zh",
            "zh-hk": "zh",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
        }

        detected_lang = lang_mapping.get(main_lang, main_lang)

        return detected_lang, confidence

    except LangDetectException:
        return "unknown", 0.0


def get_optimal_ocr_configs(
    detected_language: str, confidence: float
) -> List[Dict[str, Any]]:
    """
    根据检测到的语言类型获取最优OCR配置

    Args:
        detected_language: 检测到的语言类型
        confidence: 语言检测置信度

    Returns:
        List[Dict[str, Any]]: 最优OCR配置列表
    """
    # 如果置信度低于阈值，使用回退配置
    if confidence < LANGUAGE_DETECTION_CONFIG["confidence_threshold"]:
        if LANGUAGE_DETECTION_CONFIG["fallback_to_mixed"]:
            return LANGUAGE_OCR_CONFIGS.get("mixed", SCAN_OCR_CONFIGS)
        else:
            return LANGUAGE_OCR_CONFIGS.get("fallback", SCAN_OCR_CONFIGS)

    # 根据检测到的语言选择配置
    if detected_language == "zh":
        return LANGUAGE_OCR_CONFIGS.get("zh", SCAN_OCR_CONFIGS)
    elif detected_language == "en":
        return LANGUAGE_OCR_CONFIGS.get("en", SCAN_OCR_CONFIGS)
    elif detected_language == "mixed":
        return LANGUAGE_OCR_CONFIGS.get("mixed", SCAN_OCR_CONFIGS)
    else:
        # 未知语言，使用回退配置
        return LANGUAGE_OCR_CONFIGS.get("fallback", SCAN_OCR_CONFIGS)


def get_sample_text_for_detection(image) -> str:
    """
    从图像中提取用于语言检测的样本文本（增强版）

    Args:
        image: PIL Image对象

    Returns:
        str: 样本文本
    """
    import pytesseract

    try:
        # 使用快速OCR配置获取样本
        sample_config = LANGUAGE_DETECTION_CONFIG["sample_ocr_config"]
        custom_config = f'--psm {sample_config["psm"]} --dpi {sample_config["dpi"]}'

        # 执行快速OCR
        sample_text = pytesseract.image_to_string(
            image, lang=sample_config["lang"], config=custom_config
        )

        # 清理和截取样本
        sample_text = sample_text.strip()

        # 如果文本太短，尝试使用更高DPI的配置
        if (
            len(sample_text)
            < LANGUAGE_DETECTION_CONFIG["min_text_length_for_detection"]
        ):
            # 使用更高DPI的配置重新提取
            high_dpi_config = f'--psm {sample_config["psm"]} --dpi 200'
            high_dpi_text = pytesseract.image_to_string(
                image, lang=sample_config["lang"], config=high_dpi_config
            )

            if len(high_dpi_text.strip()) > len(sample_text):
                sample_text = high_dpi_text.strip()

        # 如果文本太长，只取前300个字符（增加长度）
        if len(sample_text) > 300:
            sample_text = sample_text[:300]

        # 清理特殊字符，保留中英文字符和基本标点
        import re

        sample_text = re.sub(r"[^\u4e00-\u9fff\w\s.,!?;:()（）]", "", sample_text)

        return sample_text

    except Exception as e:
        print(f"⚠️ 样本文本提取失败: {e}")
        return ""


def analyze_language_distribution(text: str) -> Dict[str, float]:
    """
    分析文本中的语言分布

    Args:
        text: 待分析的文本

    Returns:
        Dict[str, float]: 语言分布统计
    """
    if not text:
        return {}

    # 统计中文字符
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))

    # 统计英文字符
    english_chars = len(re.findall(r"[a-zA-Z]", text))

    # 统计数字
    digits = len(re.findall(r"\d", text))

    # 统计其他字符
    other_chars = len(text) - chinese_chars - english_chars - digits

    total_chars = len(text)

    if total_chars == 0:
        return {}

    return {
        "chinese": chinese_chars / total_chars,
        "english": english_chars / total_chars,
        "digits": digits / total_chars,
        "other": other_chars / total_chars,
        "total_chars": total_chars,
    }
