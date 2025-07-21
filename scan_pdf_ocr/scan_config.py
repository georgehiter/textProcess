"""
扫描版PDF识别专用配置文件
基于Tesseract官方最佳实践优化
"""

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


def select_chinese_ocr_config(document_type: str) -> dict:
    """
    根据文档类型智能选择中文OCR配置

    Args:
        document_type: 文档类型

    Returns:
        dict: 选定的OCR配置
    """
    config_mapping = {
        "academic": CHINESE_OCR_BEST_PRACTICES["academic_paper"],
        "table": CHINESE_OCR_BEST_PRACTICES["table_document"],
        "chinese_only": CHINESE_OCR_BEST_PRACTICES["chinese_only"],
        "batch": CHINESE_OCR_BEST_PRACTICES["fast_processing"],
        "technical": CHINESE_OCR_BEST_PRACTICES["technical_doc"],
    }

    selected_config = config_mapping.get(document_type, DEFAULT_CHINESE_OCR_CONFIG)

    print(f"🎯 智能配置选择: 文档类型={document_type}")
    print(f"📋 选择配置: {selected_config['name']}")
    print(f"📋 配置描述: {selected_config['description']}")
    print(f"🔧 PSM模式: {selected_config['psm']}")
    print(f"🔧 DPI设置: {selected_config['dpi']}")
    print(f"🔧 语言模型: {selected_config['lang']}")

    return selected_config
