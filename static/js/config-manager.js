/**
 * 配置管理器 - 处理配置格式的验证和管理
 */

class ConfigManager {
    constructor() {
        this.apiBase = '/api'
        this.presets = null
        this.currentConfig = null
        this.selectedMode = null  // 'text' 或 'scan'
        this.textConfig = null   // 文本型PDF的配置
    }

    /**
     * 初始化配置管理器
     */
    async init() {
        try {
            await this.loadPresets()
            return true
        } catch (error) {
            console.error('配置管理器初始化失败:', error)
            return false
        }
    }

    /**
     * 加载配置预设
     */
    async loadPresets() {
        try {
            const response = await fetch(`${this.apiBase}/config-presets`)
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }

            const data = await response.json()
            this.presets = data.presets
            return this.presets
        } catch (error) {
            console.error('加载配置预设失败:', error)
            throw error
        }
    }

    /**
     * 选择转换模式
     */
    selectMode(mode) {
        this.selectedMode = mode
        if (mode === 'text') {
            // 文本型PDF - 加载默认配置
            this.loadTextConfig()
        } else {
            // 扫描型PDF - 使用固定配置
            this.currentConfig = this.getDefaultScanConfig()
        }
    }

    /**
     * 加载文本型PDF配置
     */
    async loadTextConfig() {
        try {
            const preset = this.getPreset('text_pdf')
            this.textConfig = preset.config
            this.currentConfig = { ...this.textConfig }
        } catch (error) {
            console.error('加载文本型PDF配置失败:', error)
            this.currentConfig = this.getDefaultTextConfig()
        }
    }

    /**
     * 获取默认文本型PDF配置
     */
    getDefaultTextConfig() {
        return {
            conversion_mode: 'marker',
            output_format: 'markdown',
            use_llm: false,
            force_ocr: false,
            strip_existing_ocr: true,
            save_images: false,
            format_lines: false,
            disable_image_extraction: true,
            gpu: { enabled: false, num_devices: 1, num_workers: 4 }
        }
    }

    /**
     * 获取默认扫描型PDF配置
     */
    getDefaultScanConfig() {
        return {
            conversion_mode: 'ocr',
            output_format: 'markdown',
            enhance_quality: true,
            language_detection: true,
            document_type_detection: true,
            ocr_quality: 'balanced',
            target_languages: ['chi_sim', 'eng']
        }
    }

    /**
     * 更新文本型PDF配置
     */
    updateTextConfig(newConfig) {
        if (this.selectedMode === 'text') {
            this.currentConfig = { ...this.textConfig, ...newConfig }
        }
    }

    /**
     * 获取当前配置
     */
    getCurrentConfig() {
        return this.currentConfig
    }

    /**
     * 启动转换
     */
    async startConversion(taskId) {
        const config = this.getCurrentConfig()
        return await this.convertWithConfig(taskId, config)
    }

    /**
     * 使用配置进行转换
     */
    async convertWithConfig(taskId, config) {
        try {
            const response = await fetch(`${this.apiBase}/convert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    task_id: taskId,
                    config: config
                })
            })

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }

            return await response.json()
        } catch (error) {
            console.error('转换失败:', error)
            throw error
        }
    }

    /**
     * 获取预设配置
     */
    getPreset(presetName) {
        if (!this.presets) {
            throw new Error('配置预设未加载')
        }

        const preset = this.presets.find(p => p.name === presetName)
        if (!preset) {
            throw new Error(`未找到预设: ${presetName}`)
        }

        return preset.config
    }

    /**
     * 验证配置
     */
    async validateConfig(config) {
        try {
            const response = await fetch(`${this.apiBase}/validate-config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }

            return await response.json()
        } catch (error) {
            console.error('配置验证失败:', error)
            throw error
        }
    }

    /**
     * 检查配置兼容性
     */
    async checkCompatibility(config) {
        try {
            const response = await fetch(`${this.apiBase}/check-compatibility`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }

            return await response.json()
        } catch (error) {
            console.error('兼容性检查失败:', error)
            throw error
        }
    }

    /**
     * 自动修复配置
     */
    async autoFixConfig(config) {
        try {
            const response = await fetch(`${this.apiBase}/auto-fix-config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }

            return await response.json()
        } catch (error) {
            console.error('配置自动修复失败:', error)
            throw error
        }
    }

    /**
     * 检测配置版本（已简化）
     */
    detectConfigVersion(config) {
        return 'current'  // 当前配置格式
    }

    /**
     * 创建默认配置
     */
    createDefaultConfig(conversionMode = 'marker') {
        if (conversionMode === 'marker') {
            return {
                conversion_mode: 'marker',
                output_format: 'markdown',
                use_llm: false,
                force_ocr: false,
                strip_existing_ocr: true,
                save_images: false,
                format_lines: false,
                disable_image_extraction: true,
                gpu: {
                    enabled: false,
                    num_devices: 1,
                    num_workers: 4,
                    torch_device: 'cuda',
                    cuda_visible_devices: '0'
                }
            }
        } else if (conversionMode === 'ocr') {
            return {
                conversion_mode: 'ocr',
                output_format: 'markdown',
                enhance_quality: true,
                language_detection: true,
                document_type_detection: true,
                ocr_quality: 'balanced',
                target_languages: ['chi_sim', 'eng']
            }
        }

        throw new Error(`不支持的转换模式: ${conversionMode}`)
    }

    /**
     * 获取配置摘要
     */
    getConfigSummary(config) {
        const mode = config.conversion_mode || 'marker'
        const format = config.output_format || 'markdown'

        let summary = `${mode.toUpperCase()}模式 - 输出:${format}`

        if (mode === 'marker') {
            const gpuEnabled = config.gpu?.enabled
            const llmEnabled = config.use_llm
            summary += ` (GPU:${gpuEnabled ? '启用' : '禁用'}, LLM:${llmEnabled ? '启用' : '禁用'})`
        } else if (mode === 'ocr') {
            const quality = config.ocr_quality || 'balanced'
            summary += ` (质量:${quality})`
        }

        return summary
    }

    /**
     * 应用配置预设
     */
    async applyPreset(presetName) {
        try {
            const presetConfig = this.getPreset(presetName)
            this.currentConfig = presetConfig

            // 验证配置
            const validation = await this.validateConfig(presetConfig)
            if (!validation.valid) {
                console.warn('预设配置验证失败:', validation.errors)
            }

            return {
                config: presetConfig,
                validation: validation
            }
        } catch (error) {
            console.error('应用预设失败:', error)
            throw error
        }
    }

    /**
     * 智能配置建议
     */
    getConfigSuggestions(config) {
        const suggestions = []

        if (config.conversion_mode === 'marker') {
            const gpuEnabled = config.gpu?.enabled

            if (gpuEnabled) {
                suggestions.push('GPU已启用，确保系统支持CUDA以获得最佳性能')
            }

            if (config.use_llm) {
                suggestions.push('LLM已启用，转换时间可能较长但质量更高')
            }

            if (!config.disable_image_extraction) {
                suggestions.push('图片提取已启用，可能影响转换速度')
            }
        } else if (config.conversion_mode === 'ocr') {
            const quality = config.ocr_quality || 'balanced'
            if (quality === 'accurate') {
                suggestions.push('使用高精度OCR模式，转换时间较长但准确率更高')
            } else if (quality === 'fast') {
                suggestions.push('使用快速OCR模式，转换速度快但准确率可能较低')
            }

            const languages = config.target_languages || []
            if (languages.length > 2) {
                suggestions.push('目标语言较多，可能影响识别速度')
            }
        }

        return suggestions
    }
}

// 导出配置管理器
window.ConfigManager = ConfigManager 