#!/usr/bin/env python3
"""
依赖检查脚本
"""


def check_imports():
    """检查必要的导入"""
    print("🔍 检查依赖...")

    try:
        import fastapi

        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False

    try:
        import uvicorn

        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Uvicorn: {e}")
        return False

    try:
        import marker

        print("✅ Marker PDF")
    except ImportError as e:
        print(f"❌ Marker PDF: {e}")
        return False

    try:
        from fastapi.staticfiles import StaticFiles

        print("✅ StaticFiles")
    except ImportError as e:
        print(f"❌ StaticFiles: {e}")
        return False

    try:
        from fastapi.middleware.cors import CORSMiddleware

        print("✅ CORSMiddleware")
    except ImportError as e:
        print(f"❌ CORSMiddleware: {e}")
        return False

    return True


def check_files():
    """检查必要文件"""
    print("\n📁 检查文件...")

    import os

    files = [
        "main.py",
        "static/index.html",
        "static/app.js",
        "static/style.css",
        "api/routes.py",
        "api/models.py",
        "core/config.py",
        "core/converter.py",
        "utils/file_handler.py",
        "utils/progress.py",
    ]

    all_exist = True
    for file_path in files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False

    return all_exist


def main():
    """主函数"""
    print("🚀 开始依赖检查")
    print("=" * 50)

    deps_ok = check_imports()
    files_ok = check_files()

    print("\n" + "=" * 50)
    if deps_ok and files_ok:
        print("🎉 所有依赖和文件都正常")
        print("💡 可以尝试启动服务器:")
        print("   poetry run python main.py")
    else:
        print("❌ 发现问题，请检查依赖和文件")
        if not deps_ok:
            print("💡 尝试安装依赖:")
            print("   poetry install")
        if not files_ok:
            print("💡 检查项目文件是否完整")


if __name__ == "__main__":
    main()
