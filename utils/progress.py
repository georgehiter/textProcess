from typing import Dict, Any, Optional


class ProgressManager:
    """进度管理器"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def start_task(self, task_id: str, total_stages: int = 1):
        """开始任务"""
        self.tasks[task_id] = {
            "status": "processing",
            "progress": 0.0,
            "error": None,
        }

    def update_progress(self, task_id: str, progress: float):
        """只更新进度"""
        if task_id not in self.tasks:
            return

        self.tasks[task_id]["progress"] = max(0.0, min(100.0, progress))

    def complete_task(self, task_id: str, message: str = "任务完成"):
        """完成任务"""
        if task_id not in self.tasks:
            return

        self.tasks[task_id].update(
            {
                "status": "completed",
                "progress": 100.0,
            }
        )

    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        if task_id not in self.tasks:
            return

        self.tasks[task_id].update({"status": "failed", "error": error})

    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务进度"""
        return self.tasks.get(task_id)

    def remove_task(self, task_id: str):
        """移除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]


class ProgressCallback:
    """进度回调类"""

    def __init__(self, task_id: str, progress_manager: ProgressManager):
        self.task_id = task_id
        self.progress_manager = progress_manager

    def __call__(self, progress: float):
        """进度回调"""
        self.progress_manager.update_progress(self.task_id, progress)


# 全局进度管理器实例
progress_manager = ProgressManager()
