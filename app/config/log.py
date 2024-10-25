import logging
from datetime import datetime
from pathlib import Path

def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("service_logger")
    logger.setLevel(logging.INFO)

    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/{current_date}.log"

    file_handler = logging.FileHandler(
        log_file,
        encoding='utf-8'
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger