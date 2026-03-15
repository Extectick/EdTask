from .auth import router as auth_router
from .master.user.create import router as user_create_router
from .master.user.delete import router as user_delete_router
from .master.students import router as students_router
from .master.task.create import router as task_create_router
from .master.task.read import router as task_read_router
from .master.task.update import router as task_update_router
from .master.task.delete import router as task_delete_router
from .user.task.get import router as user_task_get_router
from .user.answer.create import router as answer_create_router
from .user.answer.read import router as answer_read_router
from .user.answer.update import router as answer_update_router
from .user.answer.delete import router as answer_delete_router
from .file.image.create import router as image_create_router
from .file.image.delete import router as image_delete_router
from .file.file.create import router as file_create_router
from .file.file.delete import router as file_delete_router

all_routers = [
    auth_router,
    user_create_router,
    user_delete_router,
    students_router,
    task_create_router,
    task_read_router,
    task_update_router,
    task_delete_router,
    user_task_get_router,
    answer_create_router,
    answer_read_router,
    answer_update_router,
    answer_delete_router,
    image_create_router,
    image_delete_router,
    file_create_router,
    file_delete_router,
]
