from .user.create import router as user_create_router
from .user.delete import router as user_delete_router
from .task.create import router as task_create_router
from .task.read import router as task_read_router
from .task.update import router as task_update_router
from .task.delete import router as task_delete_router
from .students import router as students_router

__all__ = [
    "user_create_router",
    "user_delete_router",
    "task_create_router",
    "task_read_router",
    "task_update_router",
    "task_delete_router",
    "students_router",
]
