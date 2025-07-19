#!/usr/bin/env python3
"""
API测试脚本
"""

import requests
import time


def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:8000/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")

        if response.status_code == 200:
            print("✅ 健康检查接口正常")
        else:
            print("❌ 健康检查接口异常")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_root_endpoint():
    """测试根路径接口"""
    print("\n🔍 测试根路径接口")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:8000/")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")

        if response.status_code == 200:
            print("✅ 根路径接口正常")
        else:
            print("❌ 根路径接口异常")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_docs_endpoint():
    """测试文档接口"""
    print("\n🔍 测试文档接口")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ 文档接口正常")
            print("📖 可以访问 http://localhost:8000/docs 查看API文档")
        else:
            print("❌ 文档接口异常")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_static_files():
    """测试静态文件"""
    print("\n🔍 测试静态文件")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:8000/static/index.html")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ 静态文件正常")
            print("🌐 可以访问 http://localhost:8000 查看Web界面")
        else:
            print("❌ 静态文件异常")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


def main():
    """主测试函数"""
    print("🚀 开始API测试")
    print("=" * 50)

    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)

    # 执行测试
    test_health_check()
    test_root_endpoint()
    test_docs_endpoint()
    test_static_files()

    print("\n" + "=" * 50)
    print("🎉 测试完成")
    print("\n📋 访问地址:")
    print("  - Web界面: http://localhost:8000")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/api/health")


if __name__ == "__main__":
    main()
