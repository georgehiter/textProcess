/**
 * 配置管理器 - 处理新旧配置格式的转换和验证
 */

class ConfigManager {
    constructor() {
        this.apiBase = '/api/v2'
        this.presets = null
        this.currentConfig = null
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
     * 检测配置版本
     */
    detectConfigVersion(config) {
        if (config.conversion_mode && config.gpu && typeof config.gpu === 'object') {
            return 'v2'
        } else if (config.conversion_mode && config.gpu_config && typeof config.gpu_config === 'object') {
            return 'v1'
        } else {
            return 'unknown'
        }
    }

    /**
     * 将V1配置转换为V2格式
     */
    convertV1ToV2(v1Config) {
        const v2Config = {
            conversion_mode: v1Config.conversion_mode || 'marker',
            output_format: v1Config.output_format || 'markdown'
        }

        if (v1Config.conversion_mode === 'marker') {
            // Marker配置
            Object.assign(v2Config, {
                use_llm: v1Config.use_llm || false,
                force_ocr: v1Config.force_ocr || false,
                strip_existing_ocr: v1Config.strip_existing_ocr !== false,
                save_images: v1Config.save_images || false,
                format_lines: v1Config.format_lines || false,
                disable_image_extraction: v1Config.disable_image_extraction !== false,
                gpu: {
                    enabled: v1Config.gpu_config?.enabled || false,
                    num_devices: v1Config.gpu_config?.num_devices || 1,
                    num_workers: v1Config.gpu_config?.num_workers || 4,
                    torch_device: v1Config.gpu_config?.torch_device || 'cuda',
                    cuda_visible_devices: v1Config.gpu_config?.cuda_visible_devices || '0'
                }
            })
        } else if (v1Config.conversion_mode === 'ocr') {
            // OCR配置
            Object.assign(v2Config, {
                enhance_quality: v1Config.enhance_quality !== false,
                language_detection: v1Config.language_detection !== false,
                document_type_detection: v1Config.document_type_detection !== false,
                ocr_quality: v1Config.ocr_quality || 'balanced',
                target_languages: v1Config.target_languages || ['chi_sim', 'eng']
            })
        }

        return v2Config
    }

    /**
     * 将V2配置转换为V1格式（用于兼容性）
     */
    convertV2ToV1(v2Config) {
        const v1Config = {
            conversion_mode: v2Config.conversion_mode || 'marker',
            output_format: v2Config.output_format || 'markdown'
        }

        if (v2Config.conversion_mode === 'marker') {
            // Marker配置
            Object.assign(v1Config, {
                use_llm: v2Config.use_llm || false,
                force_ocr: v2Config.force_ocr || false,
                strip_existing_ocr: v2Config.strip_existing_ocr !== false,
                save_images: v2Config.save_images || false,
                format_lines: v2Config.format_lines || false,
                disable_image_extraction: v2Config.disable_image_extraction !== false,
                gpu_config: {
                    enabled: v2Config.gpu?.enabled || false,
                    num_devices: v2Config.gpu?.num_devices || 1,
                    num_workers: v2Config.gpu?.num_workers || 4,
                    torch_device: v2Config.gpu?.torch_device || 'cuda',
                    cuda_visible_devices: v2Config.gpu?.cuda_visible_devices || '0'
                }
            })
        } else if (v2Config.conversion_mode === 'ocr') {
            // OCR配置
            Object.assign(v1Config, {
                enhance_quality: v2Config.enhance_quality !== false,
                language_detection: v2Config.language_detection !== false,
                document_type_detection: v2Config.document_type_detection !== false,
                ocr_quality: v2Config.ocr_quality || 'balanced',
                target_languages: v2Config.target_languages || ['chi_sim', 'eng']
            })
        }

        return v1Config
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
        const version = this.detectConfigVersion(config)
        const mode = config.conversion_mode || 'marker'
        const format = config.output_format || 'markdown'

        let summary = `V${version} ${mode.toUpperCase()}模式 - 输出:${format}`

        if (mode === 'marker') {
            const gpuEnabled = version === 'v1'
                ? config.gpu_config?.enabled
                : config.gpu?.enabled
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
        const version = this.detectConfigVersion(config)

        if (version === 'v1') {
            suggestions.push('建议升级到V2配置格式以获得更好的类型安全')
        }

        if (config.conversion_mode === 'marker') {
            const gpuEnabled = version === 'v1'
                ? config.gpu_config?.enabled
                : config.gpu?.enabled

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