from aiogram import Router

from .business import router as business_router
from .courier import router as courier_router
from .delivery import router as delivery_router
from .help import router as help_router
from .start import router as start_router

router = Router()

router.include_router(start_router)
router.include_router(business_router)
router.include_router(courier_router)
router.include_router(delivery_router)
router.include_router(help_router)
