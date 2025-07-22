const { createApp, ref, reactive, computed, onMounted, nextTick } = Vue

createApp({
    setup() {
        // 响应式数据
        const uploadedFile = ref(null)
        const isDragOver = ref(false)
        const taskId = ref(null)
        const progress = ref(0)
        const startTime = ref(null)
        const currentTime = ref(Date.now())
        const finalTime = ref(null)
        const error = ref('')
        const processingTime = ref(0)
        const textPreview = ref('')
        const gpuStatus = ref(null)
        const isConverting = ref(false)
        const showResult = ref(false)
        const hasImages = ref(false)
        const imageCount = ref(0)

        // 配置管理器
        const configManager = ref(null)
        const selectedPreset = ref(null)
        const configValidation = ref(null)
        const configSummary = ref('')

        // 转换配置 - 使用V2格式
        const config = reactive({
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
                torch_device: "cuda",
                cuda_visible_devices: "0"
            },
            // OCR配置字段
            enhance_quality: true,
            language_detection: true,
            document_type_detection: true,
            ocr_quality: 'balanced',
            target_languages: ['chi_sim', 'eng']
        })

        // 进度轮询定时器
        let progressTimer = null
        let timeUpdateTimer = null

        // 计算属性
        const renderedPreview = computed(() => {
            if (!textPreview.value) return ''

            let processedText = textPreview.value
            if (taskId.value) {
                processedText = processedText.replace(
                    /!\[([^\]]*)\]\(([^)]+)\)/g,
                    (match, alt, path) => {
                        if (!path.startsWith('http')) {
                            const filename = path.split('/').pop()
                            return `![${alt}](/api/images/${taskId.value}/${filename})`
                        }
                        return match
                    }
                )
            }

            return marked.parse(processedText)
        })

        const elapsedTime = computed(() => {
            if (!startTime.value) return '0.0秒'

            const endTime = finalTime.value || currentTime.value
            const elapsed = (endTime - startTime.value) / 1000

            if (elapsed < 60) {
                return `${elapsed.toFixed(1)}秒`
            } else {
                const minutes = Math.floor(elapsed / 60)
                const seconds = elapsed % 60
                return `${minutes}分${seconds.toFixed(0)}秒`
            }
        })

        // 工具函数
        const formatFileSize = (bytes) => {
            if (bytes === 0) return '0 Bytes'
            const k = 1024
            const sizes = ['Bytes', 'KB', 'MB', 'GB']
            const i = Math.floor(Math.log(bytes) / Math.log(k))
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
        }

        const loadGPUStatus = async () => {
            try {
                const response = await fetch('/api/gpu-status')
                if (response.ok) {
                    gpuStatus.value = await response.json()
                }
            } catch (error) {
                console.error('加载GPU状态失败:', error)
            }
        }

        // 配置管理函数
        const initConfigManager = async () => {
            try {
                configManager.value = new ConfigManager()
                const success = await configManager.value.init()
                if (success) {
                    console.log('配置管理器初始化成功')
                    // 应用默认预设
                    await selectPreset('快速Marker转换')
                }
            } catch (error) {
                console.error('配置管理器初始化失败:', error)
            }
        }

        const selectPreset = async (presetName) => {
            try {
                if (!configManager.value) return

                const result = await configManager.value.applyPreset(presetName)
                Object.assign(config, result.config)
                selectedPreset.value = presetName
                configValidation.value = result.validation
                configSummary.value = configManager.value.getConfigSummary(config)

                console.log(`应用预设: ${presetName}`)
            } catch (error) {
                console.error('应用预设失败:', error)
                showError(`应用预设失败: ${error.message}`)
            }
        }

        const switchConversionMode = async (mode) => {
            config.conversion_mode = mode

            // 根据模式选择默认预设
            if (mode === 'marker') {
                await selectPreset('快速Marker转换')
            } else if (mode === 'ocr') {
                await selectPreset('快速OCR转换')
            }
        }

        const validateCurrentConfig = async () => {
            try {
                if (!configManager.value) return

                const validation = await configManager.value.validateConfig(config)
                configValidation.value = validation
                configSummary.value = configManager.value.getConfigSummary(config)

                if (!validation.valid) {
                    showError(`配置验证失败: ${validation.errors.join(', ')}`)
                } else {
                    console.log('配置验证通过')
                }
            } catch (error) {
                console.error('配置验证失败:', error)
                showError(`配置验证失败: ${error.message}`)
            }
        }

        const resetConfig = () => {
            // 重置为默认配置
            Object.assign(config, configManager.value?.createDefaultConfig(config.conversion_mode) || {
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
                    torch_device: "cuda",
                    cuda_visible_devices: "0"
                }
            })

            selectedPreset.value = null
            configValidation.value = null
            configSummary.value = ''
        }

        const getPresetIcon = (presetName) => {
            const icons = {
                '快速Marker转换': '🚀',
                'GPU加速Marker转换': '🔥',
                '高精度OCR转换': '🎯',
                '快速OCR转换': '⚡'
            }
            return icons[presetName] || '⚙️'
        }

        // 文件处理函数
        const handleDragOver = (e) => {
            e.preventDefault()
            isDragOver.value = true
        }

        const handleDragLeave = (e) => {
            e.preventDefault()
            isDragOver.value = false
        }

        const handleDrop = (e) => {
            e.preventDefault()
            isDragOver.value = false

            const files = e.dataTransfer.files
            if (files.length > 0) {
                handleFile(files[0])
            }
        }

        const handleFileSelect = (e) => {
            const file = e.target.files[0]
            if (file) {
                handleFile(file)
            }
        }

        const handleFile = (file) => {
            if (file.type !== 'application/pdf') {
                showError('请选择PDF文件')
                return
            }

            if (file.size > 100 * 1024 * 1024) {
                showError('文件大小不能超过100MB')
                return
            }

            uploadedFile.value = file
            clearError()
        }

        const removeFile = () => {
            uploadedFile.value = null
            clearError()
        }

        const uploadFile = async () => {
            if (!uploadedFile.value) {
                showError('请先选择文件')
                return
            }

            const formData = new FormData()
            formData.append('file', uploadedFile.value)

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                })

                if (!response.ok) {
                    throw new Error(`上传失败: ${response.status}`)
                }

                const result = await response.json()
                if (result.success) {
                    taskId.value = result.task_id
                    return true
                } else {
                    throw new Error(result.message || '上传失败')
                }
            } catch (error) {
                showError(`文件上传失败: ${error.message}`)
                return false
            }
        }

        // 转换函数
        const startConversion = async () => {
            if (!uploadedFile.value) {
                showError('请先选择文件')
                return
            }

            try {
                // 验证配置
                await validateCurrentConfig()
                if (configValidation.value && !configValidation.value.valid) {
                    showError('配置验证失败，请检查配置')
                    return
                }

                // 上传文件
                const uploadSuccess = await uploadFile()
                if (!uploadSuccess) return

                // 开始转换
                isConverting.value = true
                startTime.value = Date.now()
                clearError()

                const response = await fetch('/api/v2/convert-v2', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        task_id: taskId.value,
                        config: config
                    })
                })

                if (!response.ok) {
                    throw new Error(`转换失败: ${response.status}`)
                }

                const result = await response.json()
                if (result.success) {
                    startProgressPolling()
                } else {
                    throw new Error(result.message || '转换失败')
                }
            } catch (error) {
                showError(`转换失败: ${error.message}`)
                isConverting.value = false
            }
        }

        const startProgressPolling = () => {
            if (progressTimer) clearInterval(progressTimer)
            if (timeUpdateTimer) clearInterval(timeUpdateTimer)

            progressTimer = setInterval(async () => {
                try {
                    const response = await fetch(`/api/progress/${taskId.value}`)
                    if (response.ok) {
                        const data = await response.json()
                        progress.value = data.progress || 0

                        if (data.status === 'completed') {
                            finalTime.value = Date.now()
                            processingTime.value = (finalTime.value - startTime.value) / 1000
                            await getResult()
                        } else if (data.status === 'failed') {
                            throw new Error(data.error || '转换失败')
                        }
                    }
                } catch (error) {
                    showError(`进度查询失败: ${error.message}`)
                    clearInterval(progressTimer)
                    isConverting.value = false
                }
            }, 1000)

            timeUpdateTimer = setInterval(() => {
                currentTime.value = Date.now()
            }, 100)
        }

        const getResult = async () => {
            try {
                const response = await fetch(`/api/result/${taskId.value}`)
                if (response.ok) {
                    const data = await response.json()
                    textPreview.value = data.content || ''
                    hasImages.value = data.has_images || false
                    imageCount.value = data.image_count || 0
                    showResult.value = true
                }
            } catch (error) {
                showError(`获取结果失败: ${error.message}`)
            } finally {
                isConverting.value = false
                if (progressTimer) clearInterval(progressTimer)
                if (timeUpdateTimer) clearInterval(timeUpdateTimer)
            }
        }

        const downloadResult = async () => {
            try {
                const response = await fetch(`/api/download/${taskId.value}`)
                if (response.ok) {
                    const blob = await response.blob()
                    const url = window.URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `${uploadedFile.value.name.replace('.pdf', '')}_转换.md`
                    document.body.appendChild(a)
                    a.click()
                    document.body.removeChild(a)
                    window.URL.revokeObjectURL(url)
                }
            } catch (error) {
                showError(`下载失败: ${error.message}`)
            }
        }

        const downloadImages = async () => {
            try {
                const response = await fetch(`/api/download-images/${taskId.value}`)
                if (response.ok) {
                    const blob = await response.blob()
                    const url = window.URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `${uploadedFile.value.name.replace('.pdf', '')}_图片.zip`
                    document.body.appendChild(a)
                    a.click()
                    document.body.removeChild(a)
                    window.URL.revokeObjectURL(url)
                }
            } catch (error) {
                showError(`下载图片失败: ${error.message}`)
            }
        }

        const startNewConversion = () => {
            showResult.value = false
            textPreview.value = ''
            progress.value = 0
            startTime.value = null
            finalTime.value = null
            processingTime.value = 0
            hasImages.value = false
            imageCount.value = 0
            taskId.value = null
            clearError()
        }

        const showError = (message) => {
            error.value = message
        }

        const clearError = () => {
            error.value = ''
        }

        // 生命周期
        onMounted(async () => {
            await loadGPUStatus()
            await initConfigManager()
        })

        return {
            // 响应式数据
            uploadedFile,
            isDragOver,
            taskId,
            progress,
            startTime,
            currentTime,
            finalTime,
            error,
            processingTime,
            textPreview,
            gpuStatus,
            isConverting,
            showResult,
            hasImages,
            imageCount,
            configManager,
            selectedPreset,
            configValidation,
            configSummary,

            // 配置
            config,

            // 计算属性
            renderedPreview,
            elapsedTime,

            // 工具函数
            formatFileSize,

            // 配置管理函数
            selectPreset,
            switchConversionMode,
            validateCurrentConfig,
            resetConfig,
            getPresetIcon,

            // 文件处理函数
            handleDragOver,
            handleDragLeave,
            handleDrop,
            handleFileSelect,
            removeFile,

            // 转换函数
            startConversion,
            downloadResult,
            downloadImages,
            startNewConversion,

            // 错误处理
            showError,
            clearError
        }
    }
}).mount('#app') 