#!/usr/bin/env python3
"""
简单API测试脚本 - 使用内置urllib
"""

import urllib.request
import urllib.error
import json
import time


def test_endpoint(url, name):
    """测试指定端点"""
    print(f"🔍 测试{name}")
    print("-" * 30)

    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            content = response.read().decode("utf-8")

            print(f"状态码: {status_code}")

            if status_code == 200:
                print(f"✅ {name}正常")
                if content.strip():
                    try:
                        data = json.loads(content)
                        print(f"响应: {data}")
                    except json.JSONDecodeError:
                        print(f"响应: {content[:100]}...")
            else:
                print(f"❌ {name}异常")

    except urllib.error.URLError as e:
        print(f"❌ 连接失败: {e}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def main():
    """主测试函数"""
    print("🚀 开始API测试")
    print("=" * 50)

    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)

    # 测试各个端点
    test_endpoint("http://localhost:8000/", "根路径")
    test_endpoint("http://localhost:8000/api/health", "健康检查")

    print("\n" + "=" * 50)
    print("🎉 测试完成")
    print("\n📋 访问地址:")
    print("  - Web界面: http://localhost:8000")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/api/health")


if __name__ == "__main__":
    main()
