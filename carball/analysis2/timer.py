import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def timer(process: str):
    start_time = time.time()
    try:
        yield
    finally:
        logger.info(f"{process} took {time.time() - start_time:.3f}s")
