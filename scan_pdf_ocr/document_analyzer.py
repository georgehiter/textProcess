"""
文档分析模块
用于智能检测文档类型，优化OCR配置选择
"""

import re
import numpy as np
from typing import Dict, Any
import cv2
from PIL import Image

# 导入配置文件
from .scan_config import DOCUMENT_TYPE_DETECTION_CONFIG


def detect_document_type(image: Image.Image, sample_text: str) -> str:
    """
    根据文档特征智能检测文档类型

    Args:
        image: PIL Image对象
        sample_text: 样本文本

    Returns:
        str: 文档类型 ("academic", "table", "chinese_only", "batch", "technical")
    """
    try:
        # 1. 检测表格结构
        if has_table_structure(image):
            return "table"

        # 2. 检测学术论文特征
        if has_academic_features(sample_text):
            return "academic"

        # 3. 检测纯中文文档
        if is_pure_chinese(sample_text):
            return "chinese_only"

        # 4. 检测批量处理需求
        if is_batch_processing():
            return "batch"

        # 5. 默认技术文档
        return "technical"

    except Exception as e:
        print(f"⚠️ 文档类型检测失败: {e}")
        return "technical"  # 默认回退


def has_table_structure(image: Image.Image) -> bool:
    """
    检测图像是否包含表格结构

    Args:
        image: PIL Image对象

    Returns:
        bool: 是否包含表格结构
    """
    try:
        # 转换为OpenCV格式
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # 1. 边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # 2. 直线检测
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=DOCUMENT_TYPE_DETECTION_CONFIG["table"]["line_threshold"],
            minLineLength=DOCUMENT_TYPE_DETECTION_CONFIG["table"]["min_line_length"],
            maxLineGap=DOCUMENT_TYPE_DETECTION_CONFIG["table"]["max_line_gap"],
        )

        if lines is None:
            return False

        # 3. 分析直线分布
        horizontal_lines = 0
        vertical_lines = 0

        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

            if angle < 10 or angle > 170:  # 水平线
                horizontal_lines += 1
            elif 80 < angle < 100:  # 垂直线
                vertical_lines += 1

        # 4. 判断是否为表格
        total_lines = len(lines)
        if total_lines == 0:
            return False

        horizontal_ratio = horizontal_lines / total_lines
        vertical_ratio = vertical_lines / total_lines

        # 表格特征：水平线和垂直线都较多
        table_config = DOCUMENT_TYPE_DETECTION_CONFIG["table"]
        is_table = (
            horizontal_ratio > table_config["horizontal_ratio_threshold"]
            and vertical_ratio > table_config["vertical_ratio_threshold"]
            and total_lines >= table_config["min_lines"]
        )

        print(
            f"📊 表格检测: 水平线比例={horizontal_ratio:.2f}, "
            f"垂直线比例={vertical_ratio:.2f}, 总线条数={total_lines}"
        )
        return is_table

    except Exception as e:
        print(f"⚠️ 表格结构检测失败: {e}")
        return False


def has_academic_features(text: str) -> bool:
    """
    检测文本是否包含学术论文特征

    Args:
        text: 待检测的文本

    Returns:
        bool: 是否包含学术论文特征
    """
    if not text:
        return False

    try:
        # 1. 学术论文关键词检测
        academic_keywords = DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["keywords"]
        keyword_matches = 0

        for keyword in academic_keywords:
            if keyword.lower() in text.lower():
                keyword_matches += 1

        # 2. 引用格式检测
        citation_patterns = DOCUMENT_TYPE_DETECTION_CONFIG["academic"][
            "citation_patterns"
        ]
        citation_matches = 0

        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            citation_matches += len(matches)

        # 3. 章节结构检测
        section_patterns = DOCUMENT_TYPE_DETECTION_CONFIG["academic"][
            "section_patterns"
        ]
        section_matches = 0

        for pattern in section_patterns:
            matches = re.findall(pattern, text)
            section_matches += len(matches)

        # 4. 数学公式检测
        math_patterns = DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["math_patterns"]
        math_matches = 0

        for pattern in math_patterns:
            matches = re.findall(pattern, text)
            math_matches += len(matches)

        # 5. 综合判断
        total_score = (
            keyword_matches
            * DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["keyword_weight"]
            + citation_matches
            * DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["citation_weight"]
            + section_matches
            * DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["section_weight"]
            + math_matches * DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["math_weight"]
        )

        is_academic = (
            total_score >= DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["threshold"]
        )

        print(
            f"📚 学术论文检测: 关键词匹配={keyword_matches}, 引用匹配={citation_matches}, 章节匹配={section_matches}, 公式匹配={math_matches}, 总分={total_score}"
        )
        return is_academic

    except Exception as e:
        print(f"⚠️ 学术论文特征检测失败: {e}")
        return False


def is_pure_chinese(text: str) -> bool:
    """
    检测是否为纯中文文档

    Args:
        text: 待检测的文本

    Returns:
        bool: 是否为纯中文文档
    """
    if not text:
        return False

    try:
        # 1. 字符统计
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))
        total_chars = len(text.strip())

        if total_chars == 0:
            return False

        # 2. 比例计算
        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_chars / total_chars

        # 3. 判断条件
        is_pure = (
            chinese_ratio
            >= DOCUMENT_TYPE_DETECTION_CONFIG["chinese_only"]["chinese_ratio_threshold"]
            and english_ratio
            <= DOCUMENT_TYPE_DETECTION_CONFIG["chinese_only"]["english_ratio_threshold"]
            and chinese_chars
            >= DOCUMENT_TYPE_DETECTION_CONFIG["chinese_only"]["min_chinese_chars"]
        )

        print(
            f"🇨🇳 纯中文检测: 中文字符比例={chinese_ratio:.2f}, 英文字符比例={english_ratio:.2f}, 中文字符数={chinese_chars}"
        )
        return is_pure

    except Exception as e:
        print(f"⚠️ 纯中文检测失败: {e}")
        return False


def is_batch_processing() -> bool:
    """
    检测是否为批量处理模式

    Returns:
        bool: 是否为批量处理
    """
    # 这里可以根据实际需求实现批量处理检测
    # 例如：检查文件数量、处理模式等
    # 目前返回False，后续可以根据需要扩展
    return False


def analyze_document_features(image: Image.Image, sample_text: str) -> Dict[str, Any]:
    """
    综合分析文档特征

    Args:
        image: PIL Image对象
        sample_text: 样本文本

    Returns:
        Dict[str, Any]: 文档特征分析结果
    """
    try:
        features = {
            "has_table": has_table_structure(image),
            "has_academic": has_academic_features(sample_text),
            "is_pure_chinese": is_pure_chinese(sample_text),
            "is_batch": is_batch_processing(),
            "text_length": len(sample_text),
            "chinese_ratio": len(re.findall(r"[\u4e00-\u9fff]", sample_text))
            / max(len(sample_text), 1),
            "english_ratio": len(re.findall(r"[a-zA-Z]", sample_text))
            / max(len(sample_text), 1),
        }

        # 确定文档类型
        features["document_type"] = detect_document_type(image, sample_text)

        return features

    except Exception as e:
        print(f"⚠️ 文档特征分析失败: {e}")
        return {"document_type": "technical", "error": str(e)}
