import logging
import sys

def setup_logging():
    """Sets up unified application logging to standard output."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Ensure uvicorn or standard library logging is configured nicely
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()
