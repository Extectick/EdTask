from .auth import router as auth_router
from .admin import router as admin_router
from .master import router as master_router
from .master_task import router as master_task_router

all_routers = [
    auth_router,
    admin_router,
    master_router,
    master_task_router,
]