#!/usr/bin/env python3
"""
端口测试脚本
"""

import socket


def test_port(port=8000):
    """测试端口是否可用"""
    print(f"🔍 测试端口 {port}...")

    # 检查端口是否被占用
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(("localhost", port))
        if result == 0:
            print(f"❌ 端口 {port} 已被占用")
            return False
        else:
            print(f"✅ 端口 {port} 可用")
            return True
    except Exception as e:
        print(f"❌ 端口测试失败: {e}")
        return False
    finally:
        sock.close()


def find_free_port(start_port=8000, max_attempts=10):
    """查找可用端口"""
    print(f"🔍 查找可用端口，从 {start_port} 开始...")

    for port in range(start_port, start_port + max_attempts):
        if test_port(port):
            return port

    return None


def main():
    """主函数"""
    print("🚀 端口测试")
    print("=" * 30)

    # 测试8001端口
    if test_port(8001):
        print("\n💡 建议:")
        print("1. 启动服务器:")
        print("   poetry run python main.py")
    else:
        print("\n💡 建议:")
        print("1. 检查是否有其他服务占用8001端口")
        print("2. 尝试使用其他端口:")
        print("   poetry run uvicorn main:app --port 8002")
        print("3. 或者修改配置文件中的端口设置")


if __name__ == "__main__":
    main()
