import time
from typing import Dict, Any, Optional


class ProgressManager:
    """进度管理器"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.start_times: Dict[str, float] = {}

    def start_task(self, task_id: str, total_stages: int = 1):
        """开始任务"""
        self.tasks[task_id] = {
            "status": "processing",
            "progress": 0.0,
            "current_stage": "初始化",
            "stage_progress": 0.0,
            "stage_current": 0,
            "stage_total": total_stages,
            "start_time": time.time(),
            "message": "任务已开始",
            "error": None,
        }
        self.start_times[task_id] = time.time()

    def update_progress(
        self,
        task_id: str,
        progress: float,
        stage: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """更新进度"""
        if task_id not in self.tasks:
            return

        self.tasks[task_id]["progress"] = max(0.0, min(100.0, progress))

        if stage:
            self.tasks[task_id]["current_stage"] = stage

        if message:
            self.tasks[task_id]["message"] = message

        # 计算时间信息
        elapsed = time.time() - self.start_times[task_id]
        self.tasks[task_id]["elapsed_time"] = self._format_time(elapsed)

        # 估算剩余时间
        if progress > 0:
            estimated_total = elapsed / (progress / 100)
            remaining = estimated_total - elapsed
            self.tasks[task_id]["estimated_time"] = self._format_time(remaining)

    def update_stage_progress(
        self,
        task_id: str,
        stage_current: int,
        stage_total: int,
        stage_name: Optional[str] = None,
    ):
        """更新阶段进度"""
        if task_id not in self.tasks:
            return

        self.tasks[task_id]["stage_current"] = stage_current
        self.tasks[task_id]["stage_total"] = stage_total

        if stage_total > 0:
            stage_progress = (stage_current / stage_total) * 100
            self.tasks[task_id]["stage_progress"] = stage_progress

        if stage_name:
            self.tasks[task_id]["current_stage"] = stage_name

    def complete_task(self, task_id: str, message: str = "任务完成"):
        """完成任务"""
        if task_id not in self.tasks:
            return

        self.tasks[task_id].update(
            {
                "status": "completed",
                "progress": 100.0,
                "message": message,
                "stage_progress": 100.0,
            }
        )

    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        if task_id not in self.tasks:
            return

        self.tasks[task_id].update(
            {"status": "failed", "error": error, "message": f"任务失败: {error}"}
        )

    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务进度"""
        return self.tasks.get(task_id)

    def remove_task(self, task_id: str):
        """移除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
        if task_id in self.start_times:
            del self.start_times[task_id]

    def _format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"


class ProgressCallback:
    """进度回调类"""

    def __init__(self, task_id: str, progress_manager: ProgressManager):
        self.task_id = task_id
        self.progress_manager = progress_manager

    def __call__(self, progress: float, stage: str = None, message: str = None):
        """进度回调"""
        self.progress_manager.update_progress(self.task_id, progress, stage, message)


# 全局进度管理器实例
progress_manager = ProgressManager()
