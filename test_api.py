# 创建服务实例
qwen_service = create_dashscope_qwen_service(
    api_key="your-dashscope-api-key", model_name="qwen2.5-turbo"  # 或其他支持的模型
)

# 测试连接
if qwen_service.test_connection():
    print("✓ 服务连接成功")
else:
    print("❌ 连接失败，请检查API密钥")
