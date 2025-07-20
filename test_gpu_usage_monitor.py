#!/usr/bin/env python3
"""
GPU使用情况监控测试
验证GPU是否真正被用于计算加速
"""

import os
import time
import asyncio
import psutil
import subprocess
from pathlib import Path
from core.config import settings
from core.converter import MarkerPDFConverter


class GPUUsageMonitor:
    """GPU使用情况监控器"""

    def __init__(self):
        self.test_file = None
        self.gpu_stats = []

    def find_test_file(self):
        """查找测试PDF文件"""
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            print("❌ uploads目录不存在")
            return False

        pdf_files = list(uploads_dir.glob("*.pdf"))
        if not pdf_files:
            print("❌ 未找到PDF文件")
            return False

        largest_file = max(pdf_files, key=lambda f: f.stat().st_size)
        self.test_file = str(largest_file)
        file_size_mb = largest_file.stat().st_size / (1024 * 1024)
        print(f"✅ 测试文件: {Path(self.test_file).name}")
        print(f"   文件大小: {file_size_mb:.2f} MB")
        return True

    def get_gpu_stats(self):
        """获取GPU统计信息"""
        try:
            # 使用nvidia-smi获取GPU信息
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                stats = []
                for line in lines:
                    if line.strip():
                        parts = line.split(", ")
                        if len(parts) >= 4:
                            stats.append(
                                {
                                    "gpu_util": int(parts[0]),
                                    "memory_used": int(parts[1]),
                                    "memory_total": int(parts[2]),
                                    "temperature": int(parts[3]),
                                }
                            )
                return stats
        except Exception as e:
            print(f"获取GPU统计信息失败: {e}")

        return None

    def monitor_gpu_during_conversion(self, mode="GPU"):
        """在转换过程中监控GPU使用情况"""
        print(f"\n{'='*60}")
        print(f"🔍 {mode}模式GPU使用情况监控")
        print(f"{'='*60}")

        # 配置设置
        if mode == "GPU":
            settings.GPU_ENABLED = True
            settings.GPU_DEVICES = 1
            settings.GPU_WORKERS = 4  # 较少工作进程
            # 移除批处理大小设置，使用默认配置
        else:
            settings.GPU_ENABLED = False

        settings.apply_gpu_environment()

        print(f"{mode}配置:")
        print(f"  GPU加速: {'启用' if mode == 'GPU' else '禁用'}")
        print(f"  设备数量: {settings.GPU_DEVICES}")
        print(f"  工作进程: {settings.GPU_WORKERS}")
        print(f"  批处理大小: 使用默认配置")

        # 创建转换器
        converter = MarkerPDFConverter(
            output_format="markdown",
            use_llm=False,
            force_ocr=False,
            save_images=False,
            format_lines=False,
            disable_image_extraction=True,
            strip_existing_ocr=True,
        )

        # 开始监控
        print(f"\n🚀 开始{mode}模式转换并监控GPU...")
        print("监控间隔: 每5秒记录一次GPU状态")
        print("-" * 60)

        # 清空之前的统计
        self.gpu_stats = []

        # 启动转换任务
        start_time = time.time()

        # 创建异步任务
        async def conversion_task():
            return await converter.convert_pdf_async(
                self.test_file,
                f"{mode.lower()}_monitor_test",
                f"outputs/{mode.lower()}_monitor_test",
            )

        # 启动监控线程
        import threading

        monitoring = True

        def monitor_thread():
            nonlocal monitoring
            while monitoring:
                stats = self.get_gpu_stats()
                if stats:
                    timestamp = time.time() - start_time
                    self.gpu_stats.append(
                        {"timestamp": timestamp, "stats": stats[0]}  # 假设只有一个GPU
                    )

                    gpu_util = stats[0]["gpu_util"]
                    memory_used = stats[0]["memory_used"]
                    memory_total = stats[0]["memory_total"]
                    temperature = stats[0]["temperature"]

                    print(
                        f"[{timestamp:6.1f}s] GPU利用率: {gpu_util:3d}% | "
                        f"显存: {memory_used:4d}MB/{memory_total:4d}MB | "
                        f"温度: {temperature:3d}°C"
                    )

                time.sleep(5)

        # 启动监控线程
        monitor_thread_obj = threading.Thread(target=monitor_thread)
        monitor_thread_obj.daemon = True
        monitor_thread_obj.start()

        # 执行转换
        try:
            result = asyncio.run(conversion_task())
            conversion_time = time.time() - start_time

            # 停止监控
            monitoring = False
            time.sleep(2)  # 等待监控线程结束

            if result["success"]:
                print(f"\n✅ {mode}转换成功")
                print(f"   总耗时: {conversion_time:.2f}秒")
                return True
            else:
                print(f"\n❌ {mode}转换失败: {result.get('error', '未知错误')}")
                return False

        except Exception as e:
            monitoring = False
            conversion_time = time.time() - start_time
            print(f"\n❌ {mode}转换异常: {e}")
            print(f"   耗时: {conversion_time:.2f}秒")
            return False

    def analyze_gpu_usage(self):
        """分析GPU使用情况"""
        if not self.gpu_stats:
            print("❌ 没有GPU使用数据")
            return

        print(f"\n{'='*60}")
        print("📊 GPU使用情况分析")
        print(f"{'='*60}")

        # 提取数据
        timestamps = [stat["timestamp"] for stat in self.gpu_stats]
        gpu_utils = [stat["stats"]["gpu_util"] for stat in self.gpu_stats]
        memory_useds = [stat["stats"]["memory_used"] for stat in self.gpu_stats]
        temperatures = [stat["stats"]["temperature"] for stat in self.gpu_stats]

        # 计算统计信息
        avg_gpu_util = sum(gpu_utils) / len(gpu_utils)
        max_gpu_util = max(gpu_utils)
        min_gpu_util = min(gpu_utils)

        avg_memory = sum(memory_useds) / len(memory_useds)
        max_memory = max(memory_useds)
        min_memory = min(memory_useds)

        print(f"监控时长: {timestamps[-1] - timestamps[0]:.1f}秒")
        print(f"数据点数量: {len(self.gpu_stats)}")

        print(f"\n🎯 GPU利用率:")
        print(f"  平均利用率: {avg_gpu_util:.1f}%")
        print(f"  最高利用率: {max_gpu_util}%")
        print(f"  最低利用率: {min_gpu_util}%")

        print(f"\n💾 GPU显存使用:")
        print(f"  平均使用: {avg_memory:.0f}MB")
        print(f"  最高使用: {max_memory}MB")
        print(f"  最低使用: {min_memory}MB")

        print(f"\n🌡️ GPU温度:")
        print(f"  平均温度: {sum(temperatures) / len(temperatures):.1f}°C")
        print(f"  最高温度: {max(temperatures)}°C")
        print(f"  最低温度: {min(temperatures)}°C")

        # 判断GPU是否真正被使用
        print(f"\n🔍 GPU使用判断:")
        if max_gpu_util > 10:
            print(f"  ✅ GPU真正被用于计算 (最高利用率: {max_gpu_util}%)")
        elif max_gpu_util > 5:
            print(f"  ⚠️ GPU部分被使用 (最高利用率: {max_gpu_util}%)")
        else:
            print(f"  ❌ GPU几乎没有被使用 (最高利用率: {max_gpu_util}%)")
            print(f"     可能原因:")
            print(f"     - GPU加速未正确启用")
            print(f"     - 模型未加载到GPU")
            print(f"     - 批处理大小过小")
            print(f"     - 数据预处理占用大部分时间")

        if max_memory > 1000:
            print(f"  ✅ GPU显存被大量使用 ({max_memory}MB)")
        else:
            print(f"  ⚠️ GPU显存使用较少 ({max_memory}MB)")

    def run_complete_test(self):
        """运行完整的GPU使用监控测试"""
        print("🎯 GPU使用情况监控测试")
        print("=" * 60)

        if not self.find_test_file():
            return False

        print(f"\n📋 测试计划:")
        print(f"   测试文件: {Path(self.test_file).name}")
        print(f"   监控模式: GPU模式")
        print(f"   监控间隔: 5秒")
        print(f"   监控内容: GPU利用率、显存使用、温度")

        # 运行GPU模式监控
        success = self.monitor_gpu_during_conversion("GPU")

        if success:
            self.analyze_gpu_usage()
            print(f"\n✅ GPU使用监控测试完成！")
        else:
            print(f"\n❌ GPU使用监控测试失败！")

        return success


def main():
    """主函数"""
    monitor = GPUUsageMonitor()
    monitor.run_complete_test()


if __name__ == "__main__":
    main()
