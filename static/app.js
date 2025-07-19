const { createApp, ref, reactive, computed, onMounted, nextTick } = Vue

createApp({
    setup() {
        // 响应式数据
        // const currentStep = ref(1)  // 注释掉步骤控制
        const uploadedFile = ref(null)
        const isDragOver = ref(false)
        const taskId = ref(null)
        const progress = ref(0)
        const startTime = ref(null)
        const currentTime = ref(Date.now())  // 当前时间，用于触发更新
        const finalTime = ref(null)  // 转换完成时的最终时间
        const error = ref('')
        const processingTime = ref(0)
        // const imageCount = ref(0)  // 注释掉图片计数
        const textPreview = ref('')
        const gpuStatus = ref(null)
        const isConverting = ref(false)
        const showResult = ref(false)

        // 转换配置
        const config = reactive({
            output_format: 'markdown',  // 固定为markdown格式
            // use_llm: false,        // 前端隐藏，后端保持
            force_ocr: false,
            // save_images: true,     // 前端隐藏，后端保持
            format_lines: true,
            disable_image_extraction: false,
            gpu_config: {
                enabled: true,
                devices: 1,
                workers: 4,
                memory_limit: 0.8
            }
        })

        // 进度轮询定时器
        let progressTimer = null
        // 时间更新定时器
        let timeUpdateTimer = null

        // 计算属性
        const renderedPreview = computed(() => {
            if (!textPreview.value) return ''
            return marked.parse(textPreview.value)
        })

        // 计算已用时间
        const elapsedTime = computed(() => {
            if (!startTime.value) return '0.0秒'

            // 优先使用最终时间，如果没有则使用当前时间
            const endTime = finalTime.value || currentTime.value
            const elapsed = (endTime - startTime.value) / 1000

            if (elapsed < 60) {
                return `${elapsed.toFixed(1)}秒`
            } else if (elapsed < 3600) {
                return `${(elapsed / 60).toFixed(1)}分钟`
            } else {
                return `${(elapsed / 3600).toFixed(1)}小时`
            }
        })

        // 方法
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
                const status = await response.json()
                gpuStatus.value = status

                // 如果GPU不可用，禁用GPU配置
                if (!status.available) {
                    config.gpu_config.enabled = false
                }
            } catch (err) {
                console.error('获取GPU状态失败:', err)
                gpuStatus.value = {
                    available: false,
                    device_count: 0,
                    device_name: null,
                    memory_total: null,
                    memory_used: null,
                    memory_free: null,
                    cuda_version: null,
                    pytorch_version: null,
                    current_config: config.gpu_config
                }
            }
        }

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
                const file = files[0]
                if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
                    uploadedFile.value = file
                } else {
                    showError('请选择PDF文件')
                }
            }
        }

        const handleFileSelect = (e) => {
            const file = e.target.files[0]
            if (file) {
                uploadedFile.value = file
            }
        }

        const removeFile = () => {
            uploadedFile.value = null
            if (currentStep.value > 1) {
                currentStep.value = 1
            }
        }

        const uploadFile = async () => {
            if (!uploadedFile.value) return

            try {
                const formData = new FormData()
                formData.append('file', uploadedFile.value)

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                })

                const result = await response.json()

                if (result.success) {
                    taskId.value = result.task_id
                    // currentStep.value = 2  // 删除步骤控制
                } else {
                    showError(result.message || '文件上传失败')
                }
            } catch (err) {
                showError('文件上传失败: ' + err.message)
            }
        }

        const startConversion = async () => {
            if (!uploadedFile.value) {
                showError('请先选择PDF文件')
                return
            }

            try {
                isConverting.value = true  // 设置转换状态
                showResult.value = false   // 隐藏结果
                startTime.value = Date.now()  // 记录开始时间

                // 启动时间更新定时器
                if (timeUpdateTimer) {
                    clearInterval(timeUpdateTimer)
                }
                timeUpdateTimer = setInterval(() => {
                    // 更新当前时间，触发elapsedTime重新计算
                    currentTime.value = Date.now()
                }, 1000)

                // 如果没有taskId，先上传文件
                if (!taskId.value) {
                    const formData = new FormData()
                    formData.append('file', uploadedFile.value)

                    const uploadResponse = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    })

                    const uploadResult = await uploadResponse.json()

                    if (!uploadResult.success) {
                        isConverting.value = false
                        showError(uploadResult.message || '文件上传失败')
                        return
                    }

                    taskId.value = uploadResult.task_id
                }

                // 开始转换
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        task_id: taskId.value,
                        config: {
                            ...config,
                            use_llm: false,      // 确保后端收到false
                            save_images: false   // 确保后端收到false
                        }
                    })
                })

                const result = await response.json()

                if (result.success) {
                    startProgressPolling()
                } else {
                    isConverting.value = false  // 重置状态
                    showError(result.message || '转换启动失败')
                }
            } catch (err) {
                isConverting.value = false  // 重置状态
                showError('转换启动失败: ' + err.message)
            }
        }

        const startProgressPolling = () => {
            if (progressTimer) {
                clearInterval(progressTimer)
            }

            progressTimer = setInterval(async () => {
                try {
                    const response = await fetch(`/api/progress/${taskId.value}`)
                    const data = await response.json()

                    progress.value = data.progress || 0

                    if (data.status === 'completed') {
                        clearInterval(progressTimer)
                        if (timeUpdateTimer) {
                            clearInterval(timeUpdateTimer)
                            timeUpdateTimer = null
                        }
                        finalTime.value = Date.now()  // 记录完成时间
                        isConverting.value = false  // 重置转换状态
                        await getResult()
                    } else if (data.status === 'failed') {
                        clearInterval(progressTimer)
                        if (timeUpdateTimer) {
                            clearInterval(timeUpdateTimer)
                            timeUpdateTimer = null
                        }
                        finalTime.value = Date.now()  // 记录失败时间
                        isConverting.value = false  // 重置转换状态
                        showError(data.error || '转换失败')
                    }
                } catch (err) {
                    console.error('获取进度失败:', err)
                }
            }, 1000)
        }

        const getResult = async () => {
            try {
                const response = await fetch(`/api/result/${taskId.value}`)
                const result = await response.json()

                if (result.success) {
                    // processingTime.value = result.processing_time || 0  // 不再需要后端时间
                    // imageCount.value = result.image_paths?.length || 0  // 注释掉图片计数
                    textPreview.value = result.text_preview || ''
                    showResult.value = true  // 显示结果
                    // currentStep.value = 4  // 删除步骤控制
                } else {
                    showError(result.error || '获取结果失败')
                }
            } catch (err) {
                showError('获取结果失败: ' + err.message)
            }
        }

        const downloadResult = async () => {
            if (!taskId.value) return

            try {
                const response = await fetch(`/api/download/${taskId.value}`)
                const blob = await response.blob()

                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = uploadedFile.value?.name?.replace('.pdf', '.md') || 'converted.md'
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                window.URL.revokeObjectURL(url)
            } catch (err) {
                showError('下载失败: ' + err.message)
            }
        }

        const startNewConversion = () => {
            // 重置状态
            // currentStep.value = 1  // 删除步骤控制
            uploadedFile.value = null
            taskId.value = null
            progress.value = 0
            startTime.value = null
            finalTime.value = null
            error.value = ''
            processingTime.value = 0
            // imageCount.value = 0  // 注释掉图片计数
            textPreview.value = ''
            isConverting.value = false
            showResult.value = false

            // 重置配置
            config.output_format = 'markdown'
            // config.use_llm = false  // 注释掉
            config.force_ocr = false
            // config.save_images = true  // 注释掉
            config.format_lines = true
            config.disable_image_extraction = false
            config.gpu_config.enabled = gpuStatus.value?.available || false
            config.gpu_config.devices = 1
            config.gpu_config.workers = 4
            config.gpu_config.memory_limit = 0.8

            // 清理定时器
            if (progressTimer) {
                clearInterval(progressTimer)
                progressTimer = null
            }
            if (timeUpdateTimer) {
                clearInterval(timeUpdateTimer)
                timeUpdateTimer = null
            }
        }

        const showError = (message) => {
            error.value = message
            setTimeout(() => {
                error.value = ''
            }, 5000)
        }

        const clearError = () => {
            error.value = ''
        }

        // 生命周期
        onMounted(() => {
            // 加载GPU状态
            loadGPUStatus()

            // 设置marked选项
            marked.setOptions({
                highlight: function (code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value
                        } catch (err) { }
                    }
                    return hljs.highlightAuto(code).value
                }
            })
        })

        return {
            // currentStep,  // 注释掉步骤控制
            uploadedFile,
            isDragOver,
            taskId,
            progress,
            startTime,
            currentTime,
            finalTime,
            elapsedTime,
            error,
            processingTime,
            // imageCount,  // 注释掉图片计数
            textPreview,
            gpuStatus,
            config,
            renderedPreview,
            isConverting,
            showResult,
            formatFileSize,
            handleDragOver,
            handleDragLeave,
            handleDrop,
            handleFileSelect,
            removeFile,
            uploadFile,
            startConversion,
            downloadResult,
            startNewConversion,
            showError,
            clearError
        }
    }
}).mount('#app') 