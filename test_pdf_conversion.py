#!/usr/bin/env python3
"""
PDF转换功能测试脚本
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import time
import os
from pathlib import Path


def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查接口")
    print("-" * 40)

    try:
        with urllib.request.urlopen("http://localhost:8000/api/health") as response:
            status_code = response.getcode()
            content = response.read().decode("utf-8")

            print(f"状态码: {status_code}")
            if status_code == 200:
                data = json.loads(content)
                print(f"✅ 健康检查正常: {data}")
                return True
            else:
                print(f"❌ 健康检查失败")
                return False

    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False


def test_file_upload(pdf_path):
    """测试文件上传"""
    print(f"\n📤 测试文件上传: {pdf_path}")
    print("-" * 40)

    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        return None

    try:
        # 准备multipart数据
        boundary = "boundary123"
        data = []

        # 添加文件数据
        data.append(f"--{boundary}".encode())
        data.append(b'Content-Disposition: form-data; name="file"; filename="test.pdf"')
        data.append(b"Content-Type: application/pdf")
        data.append(b"")

        with open(pdf_path, "rb") as f:
            data.append(f.read())

        data.append(f"--{boundary}--".encode())
        data.append(b"")

        # 发送请求
        request = urllib.request.Request(
            "http://localhost:8000/api/upload",
            data=b"\r\n".join(data),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )

        with urllib.request.urlopen(request) as response:
            status_code = response.getcode()
            content = response.read().decode("utf-8")

            print(f"状态码: {status_code}")
            if status_code == 200:
                result = json.loads(content)
                print(f"✅ 文件上传成功: {result}")
                return result.get("task_id")
            else:
                print(f"❌ 文件上传失败: {content}")
                return None

    except Exception as e:
        print(f"❌ 文件上传异常: {e}")
        return None


def test_conversion_start(task_id, config):
    """测试开始转换"""
    print(f"\n🔄 测试开始转换: {task_id}")
    print("-" * 40)

    try:
        data = json.dumps({"task_id": task_id, "config": config}).encode("utf-8")

        request = urllib.request.Request(
            "http://localhost:8000/api/convert",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(request) as response:
            status_code = response.getcode()
            content = response.read().decode("utf-8")

            print(f"状态码: {status_code}")
            if status_code == 200:
                result = json.loads(content)
                print(f"✅ 转换启动成功: {result}")
                return True
            else:
                print(f"❌ 转换启动失败: {content}")
                return False

    except Exception as e:
        print(f"❌ 转换启动异常: {e}")
        return False


def test_progress_monitoring(task_id, max_wait=60):
    """测试进度监控"""
    print(f"\n📊 监控转换进度: {task_id}")
    print("-" * 40)

    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            with urllib.request.urlopen(
                f"http://localhost:8000/api/progress/{task_id}"
            ) as response:
                status_code = response.getcode()
                content = response.read().decode("utf-8")

                if status_code == 200:
                    progress = json.loads(content)
                    print(
                        f"进度: {progress.get('progress', 0):.1f}% - {progress.get('current_stage', '')} - {progress.get('message', '')}"
                    )

                    if progress.get("status") == "completed":
                        print("✅ 转换完成")
                        return True
                    elif progress.get("status") == "failed":
                        print(f"❌ 转换失败: {progress.get('error', '')}")
                        return False

                else:
                    print(f"❌ 获取进度失败: {content}")
                    return False

        except Exception as e:
            print(f"❌ 进度监控异常: {e}")
            return False

        time.sleep(2)

    print("⏰ 转换超时")
    return False


def test_result_retrieval(task_id):
    """测试结果获取"""
    print(f"\n📄 获取转换结果: {task_id}")
    print("-" * 40)

    try:
        with urllib.request.urlopen(
            f"http://localhost:8000/api/result/{task_id}"
        ) as response:
            status_code = response.getcode()
            content = response.read().decode("utf-8")

            print(f"状态码: {status_code}")
            if status_code == 200:
                result = json.loads(content)
                print(f"✅ 结果获取成功")
                print(f"输出文件: {result.get('output_file', 'N/A')}")
                print(f"处理时间: {result.get('processing_time', 'N/A')}秒")
                print(f"图片数量: {len(result.get('image_paths', []))}")

                # 显示预览
                preview = result.get("text_preview", "")
                if preview:
                    print(f"内容预览: {preview[:200]}...")

                return True
            else:
                print(f"❌ 结果获取失败: {content}")
                return False

    except Exception as e:
        print(f"❌ 结果获取异常: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始PDF转换功能测试")
    print("=" * 60)

    # 检查服务状态
    if not test_health_check():
        print("❌ 服务不可用，请先启动服务")
        return

    # 查找测试PDF文件
    test_files = ["input/test.pdf", "input/sample.pdf", "test.pdf", "sample.pdf"]

    pdf_path = None
    for file_path in test_files:
        if os.path.exists(file_path):
            pdf_path = file_path
            break

    if not pdf_path:
        print("❌ 未找到测试PDF文件")
        print("请将PDF文件放在以下位置之一:")
        for path in test_files:
            print(f"  - {path}")
        return

    print(f"📄 使用测试文件: {pdf_path}")

    # 转换配置
    config = {
        "output_format": "markdown",
        "use_llm": False,
        "force_ocr": False,
        "save_images": True,
        "format_lines": True,
        "disable_image_extraction": False,
    }

    # 执行测试流程
    print(f"\n⚙️ 转换配置: {config}")

    # 1. 上传文件
    task_id = test_file_upload(pdf_path)
    if not task_id:
        print("❌ 文件上传失败，测试终止")
        return

    # 2. 开始转换
    if not test_conversion_start(task_id, config):
        print("❌ 转换启动失败，测试终止")
        return

    # 3. 监控进度
    if not test_progress_monitoring(task_id):
        print("❌ 转换失败或超时，测试终止")
        return

    # 4. 获取结果
    if not test_result_retrieval(task_id):
        print("❌ 结果获取失败，测试终止")
        return

    print("\n" + "=" * 60)
    print("🎉 PDF转换功能测试完成！")
    print("\n📋 访问地址:")
    print("  - Web界面: http://localhost:8000")
    print("  - API文档: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
