import time
import logging
from fastapi import Request
from typing import Callable

logger = logging.getLogger("service_logger")


async def logging_dependency(request: Request, call_next: Callable):
    start_time = time.time()
    logger.info(f"Request started - Method: {request.method} Path: {request.url.path}")

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Request completed - Method: {request.method} "
        f"Path: {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {process_time:.2f}ms"
    )

    return response