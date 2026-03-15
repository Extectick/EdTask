from .create import router as create_router
from .read import router as read_router
from .update import router as update_router
from .delete import router as delete_router

__all__ = ["create_router", "read_router", "update_router", "delete_router"]
