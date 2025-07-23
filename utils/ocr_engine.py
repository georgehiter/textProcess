"""
OCR智能引擎
集成配置管理、语言检测、文档分析功能
为扫描版PDF转换提供智能OCR配置选择
"""

import re
import numpy as np
from typing import Dict, Any, Tuple, List
import cv2
from PIL import Image
from langdetect import detect, detect_langs, LangDetectException
import pytesseract

# 设置Tesseract路径（Windows）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OCREngine:
    """OCR智能引擎 - 集成配置、语言检测、文档分析"""

    # ==================== 配置常量 ====================

    # 基于最佳实践的中文OCR默认配置
    CHINESE_OCR_BEST_PRACTICES = {
        # 学术论文配置 - 高质量要求
        "academic_paper": {
            "lang": "chi_sim+eng",
            "psm": 1,  # 自动页面分割+OSD
            "dpi": 400,  # 高分辨率
            "name": "academic_paper",
            "description": "学术论文、高质量文档",
        },
        # 技术文档配置 - 平衡性能
        "technical_doc": {
            "lang": "chi_sim+eng",
            "psm": 6,  # 统一文本块
            "dpi": 300,  # 标准分辨率
            "name": "technical_doc",
            "description": "技术文档、标准文档",
        },
        # 表格文档配置 - 保持结构
        "table_document": {
            "lang": "chi_sim+eng",
            "psm": 13,  # 原始行模式
            "dpi": 300,  # 标准分辨率
            "name": "table_document",
            "description": "表格、结构化文档",
        },
        # 纯中文文档配置
        "chinese_only": {
            "lang": "chi_sim",
            "psm": 1,  # 自动页面分割+OSD
            "dpi": 300,  # 标准分辨率
            "name": "chinese_only",
            "description": "纯中文文档",
        },
        # 快速处理配置 - 批量处理
        "fast_processing": {
            "lang": "chi_sim+eng",
            "psm": 6,  # 统一文本块
            "dpi": 200,  # 较低分辨率
            "name": "fast_processing",
            "description": "快速处理、批量文档",
        },
    }

    # 默认中文OCR配置 - 使用技术文档配置作为默认
    DEFAULT_CHINESE_OCR_CONFIG = CHINESE_OCR_BEST_PRACTICES["technical_doc"]

    # 英文OCR默认配置 - 使用最佳实践的标准配置
    DEFAULT_ENGLISH_OCR_CONFIG = {
        "lang": "eng",
        "psm": 6,  # 统一文本块
        "dpi": 400,  # 标准分辨率
        "name": "english_standard",
        "description": "标准英文文档配置",
    }

    # 保留原有配置用于兼容性
    SCAN_OCR_CONFIGS = [
        # 配置1：自动页面分割，中英文混合
        {"lang": "chi_sim+eng", "psm": 1, "dpi": 300, "name": "auto_page"},
        # 配置2：统一文本块，中英文混合
        {"lang": "chi_sim+eng", "psm": 6, "dpi": 300, "name": "uniform_block"},
        # 配置3：仅中文识别
        {"lang": "chi_sim", "psm": 1, "dpi": 300, "name": "chinese_only"},
    ]

    # 语言检测配置
    LANGUAGE_DETECTION_CONFIG = {
        "confidence_threshold": 0.7,  # 提高置信度阈值
        "min_text_length_for_detection": 50,  # 增加最小文本长度
        "fallback_to_mixed": True,  # 检测失败时是否回退到混合模式
        "sample_ocr_config": {  # 用于语言检测的快速OCR配置
            "lang": "chi_sim+eng",
            "psm": 1,
            "dpi": 150,  # 降低DPI以提升速度
        },
    }

    # 简化的语言OCR配置映射 - 直接使用最佳实践配置
    LANGUAGE_OCR_CONFIGS = {
        "zh": [DEFAULT_CHINESE_OCR_CONFIG],  # 中文文档使用默认配置
        "en": [DEFAULT_ENGLISH_OCR_CONFIG],  # 英文文档使用默认配置
        "mixed": [DEFAULT_CHINESE_OCR_CONFIG],  # 混合语言使用默认配置
        "fallback": [DEFAULT_CHINESE_OCR_CONFIG],  # 回退到默认配置
    }

    # 图像增强配置 - 基于最佳实践优化
    SCAN_IMAGE_ENHANCEMENT = {
        "contrast_factor": 1.3,  # 对比度增强因子
        "sharpness": True,  # 是否启用锐化
        "denoise": True,  # 是否启用去噪
        "scale_factor": 2.5,  # 图像缩放因子
        "clahe_clip_limit": 2.0,  # CLAHE对比度限制
        "clahe_tile_size": (8, 8),  # CLAHE瓦片大小
        # 新增：基于最佳实践的预处理选项
        "remove_alpha_channel": True,  # 移除透明通道
        "add_border": True,  # 添加白色边框
        "border_size": "10x10",  # 边框大小
    }

    # 文本清理配置
    SCAN_TEXT_CLEANING = {
        "remove_extra_spaces": True,  # 移除多余空格
        "normalize_newlines": True,  # 规范化换行
        "fix_common_errors": True,  # 修复常见错误
    }

    # 文件夹配置
    FOLDER_CONFIG = {
        "ocr_uploads_folder": "ocr_uploads",  # OCR上传文件夹
        "outputs_folder": "outputs",  # 输出文件夹
        "supported_extensions": [".pdf"],  # 支持的文件扩展名
    }

    # 输出配置
    SCAN_OUTPUT_CONFIG = {
        "default_encoding": "utf-8",  # 默认编码
        "include_page_breaks": True,  # 包含页面分隔符
    }

    # 输出格式配置
    OUTPUT_FORMAT_CONFIG = {
        "default_format": "md",  # 默认输出格式：md 或 txt
        "include_metadata": True,  # 是否包含元数据
        "page_headers": True,  # 是否包含页面标题
        "processing_info": True,  # 是否包含处理信息
        "separator_line": "---",  # 页面分隔符
    }

    # 文档类型检测配置
    DOCUMENT_TYPE_DETECTION_CONFIG = {
        # 表格检测配置
        "table": {
            "line_threshold": 50,  # 直线检测阈值
            "min_line_length": 50,  # 最小直线长度
            "max_line_gap": 10,  # 最大直线间隙
            "horizontal_ratio_threshold": 0.3,  # 水平线比例阈值
            "vertical_ratio_threshold": 0.2,  # 垂直线比例阈值
            "min_lines": 8,  # 最小线条数
        },
        # 学术论文检测配置
        "academic": {
            "keywords": [
                "abstract",
                "introduction",
                "conclusion",
                "references",
                "bibliography",
                "method",
                "methodology",
                "results",
                "discussion",
                "figure",
                "table",
                "equation",
                "摘要",
                "引言",
                "结论",
                "参考文献",
                "方法",
                "结果",
                "讨论",
            ],
            "citation_patterns": [
                r"\[\d+\]",  # [1], [2], etc.
                r"\(\d{4}\)",  # (2023), (2024), etc.
                r"et al\.",  # et al.
                r"参考文献",  # 中文引用
            ],
            "section_patterns": [
                r"^\d+\.\s+\w+",  # 1. Introduction
                r"^\d+\.\d+\s+\w+",  # 1.1 Background
                r"^[A-Z][a-z]+\s*$",  # Abstract, Introduction
            ],
            "math_patterns": [
                r"[α-ωΑ-Ω]",  # 希腊字母
                r"[∑∫∏√∞]",  # 数学符号
                r"\\[a-zA-Z]+",  # LaTeX命令
            ],
            "keyword_weight": 1.0,  # 关键词权重
            "citation_weight": 2.0,  # 引用权重
            "section_weight": 1.5,  # 章节权重
            "math_weight": 1.5,  # 数学公式权重
            "threshold": 3.0,  # 总分阈值
        },
        # 纯中文检测配置
        "chinese_only": {
            "chinese_ratio_threshold": 0.8,  # 中文字符比例阈值
            "english_ratio_threshold": 0.1,  # 英文字符比例阈值
            "min_chinese_chars": 20,  # 最小中文字符数
        },
        # 批量处理检测配置
        "batch": {
            "file_count_threshold": 10,  # 文件数量阈值
            "processing_mode": "batch",  # 处理模式
        },
    }

    # ==================== 语言检测方法 ====================

    @staticmethod
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
            < OCREngine.LANGUAGE_DETECTION_CONFIG["min_text_length_for_detection"]
        ):
            return "unknown", 0.0

        try:
            # 1. 字符统计验证
            char_distribution = OCREngine.analyze_language_distribution(text)

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

    @staticmethod
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
            < OCREngine.LANGUAGE_DETECTION_CONFIG["min_text_length_for_detection"]
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

    @staticmethod
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
        if confidence < OCREngine.LANGUAGE_DETECTION_CONFIG["confidence_threshold"]:
            if OCREngine.LANGUAGE_DETECTION_CONFIG["fallback_to_mixed"]:
                return OCREngine.LANGUAGE_OCR_CONFIGS.get(
                    "mixed", OCREngine.SCAN_OCR_CONFIGS
                )
            else:
                return OCREngine.LANGUAGE_OCR_CONFIGS.get(
                    "fallback", OCREngine.SCAN_OCR_CONFIGS
                )

        # 根据检测到的语言选择配置
        if detected_language == "zh":
            return OCREngine.LANGUAGE_OCR_CONFIGS.get("zh", OCREngine.SCAN_OCR_CONFIGS)
        elif detected_language == "en":
            return OCREngine.LANGUAGE_OCR_CONFIGS.get("en", OCREngine.SCAN_OCR_CONFIGS)
        elif detected_language == "mixed":
            return OCREngine.LANGUAGE_OCR_CONFIGS.get(
                "mixed", OCREngine.SCAN_OCR_CONFIGS
            )
        else:
            # 未知语言，使用回退配置
            return OCREngine.LANGUAGE_OCR_CONFIGS.get(
                "fallback", OCREngine.SCAN_OCR_CONFIGS
            )

    @staticmethod
    def get_sample_text_for_detection(image) -> str:
        """
        从图像中提取用于语言检测的样本文本（增强版）

        Args:
            image: PIL Image对象

        Returns:
            str: 样本文本
        """
        try:
            # 使用快速OCR配置获取样本
            sample_config = OCREngine.LANGUAGE_DETECTION_CONFIG["sample_ocr_config"]
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
                < OCREngine.LANGUAGE_DETECTION_CONFIG["min_text_length_for_detection"]
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
            sample_text = re.sub(r"[^\u4e00-\u9fff\w\s.,!?;:()（）]", "", sample_text)

            return sample_text

        except Exception as e:
            print(f"⚠️ 样本文本提取失败: {e}")
            return ""

    @staticmethod
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

    # ==================== 文档分析方法 ====================

    @staticmethod
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
            if OCREngine.has_table_structure(image):
                return "table"

            # 2. 检测学术论文特征
            if OCREngine.has_academic_features(sample_text):
                return "academic"

            # 3. 检测纯中文文档
            if OCREngine.is_pure_chinese(sample_text):
                return "chinese_only"

            # 4. 检测批量处理需求
            if OCREngine.is_batch_processing():
                return "batch"

            # 5. 默认技术文档
            return "technical"

        except Exception as e:
            print(f"⚠️ 文档类型检测失败: {e}")
            return "technical"  # 默认回退

    @staticmethod
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
                threshold=OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["table"][
                    "line_threshold"
                ],
                minLineLength=OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["table"][
                    "min_line_length"
                ],
                maxLineGap=OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["table"][
                    "max_line_gap"
                ],
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
            table_config = OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["table"]
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

    @staticmethod
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
            academic_keywords = OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"][
                "keywords"
            ]
            keyword_matches = 0

            for keyword in academic_keywords:
                if keyword.lower() in text.lower():
                    keyword_matches += 1

            # 2. 引用格式检测
            citation_patterns = OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"][
                "citation_patterns"
            ]
            citation_matches = 0

            for pattern in citation_patterns:
                matches = re.findall(pattern, text)
                citation_matches += len(matches)

            # 3. 章节结构检测
            section_patterns = OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"][
                "section_patterns"
            ]
            section_matches = 0

            for pattern in section_patterns:
                matches = re.findall(pattern, text)
                section_matches += len(matches)

            # 4. 数学公式检测
            math_patterns = OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"][
                "math_patterns"
            ]
            math_matches = 0

            for pattern in math_patterns:
                matches = re.findall(pattern, text)
                math_matches += len(matches)

            # 5. 综合判断
            total_score = (
                keyword_matches
                * OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["keyword_weight"]
                + citation_matches
                * OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"][
                    "citation_weight"
                ]
                + section_matches
                * OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["section_weight"]
                + math_matches
                * OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["math_weight"]
            )

            is_academic = (
                total_score
                >= OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["academic"]["threshold"]
            )

            print(
                f"📚 学术论文检测: 关键词匹配={keyword_matches}, 引用匹配={citation_matches}, "
                f"章节匹配={section_matches}, 公式匹配={math_matches}, 总分={total_score}"
            )
            return is_academic

        except Exception as e:
            print(f"⚠️ 学术论文特征检测失败: {e}")
            return False

    @staticmethod
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
                >= OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["chinese_only"][
                    "chinese_ratio_threshold"
                ]
                and english_ratio
                <= OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["chinese_only"][
                    "english_ratio_threshold"
                ]
                and chinese_chars
                >= OCREngine.DOCUMENT_TYPE_DETECTION_CONFIG["chinese_only"][
                    "min_chinese_chars"
                ]
            )

            print(
                f"🇨🇳 纯中文检测: 中文字符比例={chinese_ratio:.2f}, "
                f"英文字符比例={english_ratio:.2f}, 中文字符数={chinese_chars}"
            )
            return is_pure

        except Exception as e:
            print(f"⚠️ 纯中文检测失败: {e}")
            return False

    @staticmethod
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

    @staticmethod
    def analyze_document_features(
        image: Image.Image, sample_text: str
    ) -> Dict[str, Any]:
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
                "has_table": OCREngine.has_table_structure(image),
                "has_academic": OCREngine.has_academic_features(sample_text),
                "is_pure_chinese": OCREngine.is_pure_chinese(sample_text),
                "is_batch": OCREngine.is_batch_processing(),
                "text_length": len(sample_text),
                "chinese_ratio": len(re.findall(r"[\u4e00-\u9fff]", sample_text))
                / max(len(sample_text), 1),
                "english_ratio": len(re.findall(r"[a-zA-Z]", sample_text))
                / max(len(sample_text), 1),
            }

            # 确定文档类型
            features["document_type"] = OCREngine.detect_document_type(
                image, sample_text
            )

            return features

        except Exception as e:
            print(f"⚠️ 文档特征分析失败: {e}")
            return {"document_type": "technical", "error": str(e)}

    # ==================== 配置选择方法 ====================

    @staticmethod
    def select_chinese_ocr_config(document_type: str) -> dict:
        """
        根据文档类型智能选择中文OCR配置

        Args:
            document_type: 文档类型

        Returns:
            dict: 选定的OCR配置
        """
        config_mapping = {
            "academic": OCREngine.CHINESE_OCR_BEST_PRACTICES["academic_paper"],
            "table": OCREngine.CHINESE_OCR_BEST_PRACTICES["table_document"],
            "chinese_only": OCREngine.CHINESE_OCR_BEST_PRACTICES["chinese_only"],
            "batch": OCREngine.CHINESE_OCR_BEST_PRACTICES["fast_processing"],
            "technical": OCREngine.CHINESE_OCR_BEST_PRACTICES["technical_doc"],
        }

        selected_config = config_mapping.get(
            document_type, OCREngine.DEFAULT_CHINESE_OCR_CONFIG
        )

        print(f"🎯 智能配置选择: 文档类型={document_type}")
        print(f"📋 选择配置: {selected_config['name']}")
        print(f"📋 配置描述: {selected_config['description']}")
        print(f"🔧 PSM模式: {selected_config['psm']}")
        print(f"🔧 DPI设置: {selected_config['dpi']}")
        print(f"🔧 语言模型: {selected_config['lang']}")

        return selected_config

    # ==================== 便捷访问方法 ====================

    @staticmethod
    def get_scan_image_enhancement() -> Dict[str, Any]:
        """获取图像增强配置"""
        return OCREngine.SCAN_IMAGE_ENHANCEMENT

    @staticmethod
    def get_scan_text_cleaning() -> Dict[str, Any]:
        """获取文本清理配置"""
        return OCREngine.SCAN_TEXT_CLEANING

    @staticmethod
    def get_scan_output_config() -> Dict[str, Any]:
        """获取输出配置"""
        return OCREngine.SCAN_OUTPUT_CONFIG

    @staticmethod
    def get_output_format_config() -> Dict[str, Any]:
        """获取输出格式配置"""
        return OCREngine.OUTPUT_FORMAT_CONFIG

    @staticmethod
    def get_default_chinese_ocr_config() -> Dict[str, Any]:
        """获取默认中文OCR配置"""
        return OCREngine.DEFAULT_CHINESE_OCR_CONFIG

    @staticmethod
    def get_default_english_ocr_config() -> Dict[str, Any]:
        """获取默认英文OCR配置"""
        return OCREngine.DEFAULT_ENGLISH_OCR_CONFIG
