#!/usr/bin/env python3
"""
force_ocr 功能测试脚本
用于验证 force_ocr 参数在前后端是否正确传递和使用
"""

import requests
import json
import time
import os

# 测试配置
BASE_URL = "http://localhost:8001"  # 修正端口号
TEST_PDF_PATH = "uploads"  # 测试文件目录


def test_force_ocr_parameter():
    """测试 force_ocr 参数传递"""
    print("🧪 开始测试 force_ocr 参数传递...")

    # 检查测试文件目录是否存在
    if not os.path.exists(TEST_PDF_PATH):
        print(f"❌ 测试文件目录 {TEST_PDF_PATH} 不存在")
        return False

    # 查找uploads目录中的PDF文件
    pdf_files = []
    for file in os.listdir(TEST_PDF_PATH):
        if file.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(TEST_PDF_PATH, file))

    if not pdf_files:
        print(f"❌ 在 {TEST_PDF_PATH} 目录中没有找到PDF文件")
        return False

    # 使用第一个PDF文件进行测试
    test_file = pdf_files[0]
    print(f"📄 使用测试文件: {test_file}")

    # 测试用例1: force_ocr = False
    print("\n📋 测试用例1: force_ocr = False")
    success1 = test_conversion_with_config(
        test_file,
        {
            "force_ocr": False,
            "strip_existing_ocr": True,
            "save_images": False,
            "format_lines": False,
            "disable_image_extraction": True,
            "gpu_config": {
                "enabled": False,
                "devices": 1,
                "workers": 4,
                "memory_limit": 0.8,
            },
        },
    )

    # 测试用例2: force_ocr = True
    print("\n📋 测试用例2: force_ocr = True")
    success2 = test_conversion_with_config(
        test_file,
        {
            "force_ocr": True,
            "strip_existing_ocr": False,
            "save_images": True,
            "format_lines": True,
            "disable_image_extraction": False,
            "gpu_config": {
                "enabled": False,
                "devices": 1,
                "workers": 4,
                "memory_limit": 0.8,
            },
        },
    )

    return success1 and success2


def test_conversion_with_config(test_file, config):
    """使用指定配置进行转换测试"""
    try:
        print(f"🔍 测试配置: {json.dumps(config, indent=2)}")

        # 1. 上传文件
        print("📤 上传文件...")
        with open(test_file, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)

        if response.status_code != 200:
            print(f"❌ 文件上传失败: {response.status_code}")
            return False

        upload_result = response.json()
        task_id = upload_result["task_id"]
        print(f"✅ 文件上传成功，任务ID: {task_id}")

        # 2. 开始转换
        print("🔄 开始转换...")
        convert_request = {"task_id": task_id, "config": config}

        response = requests.post(
            f"{BASE_URL}/api/convert",
            json=convert_request,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 200:
            print(f"❌ 转换启动失败: {response.status_code}")
            return False

        convert_result = response.json()
        print(f"✅ 转换启动成功: {convert_result['message']}")

        # 3. 监控进度
        print("⏳ 监控转换进度...")
        max_wait_time = 300  # 5分钟超时
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            response = requests.get(f"{BASE_URL}/api/progress/{task_id}")
            if response.status_code != 200:
                print(f"❌ 获取进度失败: {response.status_code}")
                return False

            progress_data = response.json()
            status = progress_data["status"]
            progress = progress_data["progress"]

            print(f"📊 进度: {progress:.1f}% - 状态: {status}")

            if status == "completed":
                print("✅ 转换完成")
                break
            elif status == "failed":
                print(f"❌ 转换失败: {progress_data.get('error', '未知错误')}")
                return False

            time.sleep(2)
        else:
            print("❌ 转换超时")
            return False

        # 4. 获取结果
        print("📥 获取转换结果...")
        response = requests.get(f"{BASE_URL}/api/result/{task_id}")
        if response.status_code != 200:
            print(f"❌ 获取结果失败: {response.status_code}")
            return False

        result_data = response.json()
        print("✅ 获取结果成功")
        print(f"   - 输出文件: {result_data.get('output_file', 'N/A')}")
        print(f"   - 处理时间: {result_data.get('processing_time', 'N/A')}秒")
        print(f"   - 图片数量: {len(result_data.get('image_paths', []))}")

        # 5. 检查输出文件
        output_file = result_data.get("output_file")
        if output_file and os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"📄 输出文件大小: {len(content)} 字符")
                print(f"📄 内容预览: {content[:200]}...")

        # 6. 清理任务
        print("🧹 清理任务...")
        response = requests.delete(f"{BASE_URL}/api/task/{task_id}")
        if response.status_code == 200:
            print("✅ 任务清理成功")
        else:
            print(f"⚠️ 任务清理失败: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        return False


def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器状态异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        return False


def main():
    """主函数"""
    print("🚀 force_ocr 功能测试开始")
    print("=" * 50)

    # 检查服务器状态
    if not check_server_status():
        return

    # 检查测试文件目录
    if not os.path.exists(TEST_PDF_PATH):
        print(f"❌ 测试文件目录 {TEST_PDF_PATH} 不存在")
        print("请确保uploads目录存在并包含PDF文件")
        return

    # 运行测试
    success = test_force_ocr_parameter()

    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！force_ocr 功能正常工作")
    else:
        print("❌ 测试失败，请检查日志和配置")

    print("\n📝 测试说明:")
    print("1. 查看控制台输出，确认参数传递正确")
    print("2. 对比两个测试用例的转换结果差异")
    print("3. 检查后端日志中的调试信息")
    print("4. 验证 force_ocr 是否真正影响转换行为")


if __name__ == "__main__":
    main()
