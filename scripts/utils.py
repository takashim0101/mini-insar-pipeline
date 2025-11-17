import logging
import os
import time
import torch
from typing import Optional

LOG_DIR = os.environ.get("INSAR_LOG_DIR", "/opt/data/logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging(name: str = "mini_insar"):
    """Initializes and returns a logger."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{name}.log")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding duplicate handlers
    if not logger.handlers:
        # File handler
        fh = logging.FileHandler(log_path)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(ch)
        
    return logger

def check_gpu(logger: Optional[logging.Logger] = None):
    """Checks for GPU availability and logs details."""
    if logger is None:
        logger = logging.getLogger()

    try:
        if torch.cuda.is_available():
            cnt = torch.cuda.device_count()
            logger.info(f"PyTorch: CUDA is available. Found {cnt} GPU(s).")
            for i in range(cnt):
                logger.info(f"  - GPU {i}: {torch.cuda.get_device_name(i)}")
            return True
        else:
            logger.info("PyTorch: CUDA not available.")
            return False
    except Exception as e:
        logger.warning(f"GPU check failed: {e}")
        return False

def safe_mkdir(path: str):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    return path

def format_time(seconds: float) -> str:
    """Converts seconds into a human-readable HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"