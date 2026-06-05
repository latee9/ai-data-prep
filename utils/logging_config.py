# utils/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logging(level=logging.INFO) -> logging.Logger:
    """
    إعداد نظام السجلات للتطبيق.
    - يكتب في الملف logs/app.log (حد أقصى 2MB، يحتفظ بآخر 3 نسخ)
    - يعرض في الـ console أيضاً
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("ai_data_prep")
    logger.setLevel(level)

    if logger.handlers:
        return logger  # تجنّب إضافة handlers مكررة

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler للملف مع rotation
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Handler للـ console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # console يظهر تحذيرات وأخطاء فقط

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# logger جاهز للاستخدام في أي مكان:
# from utils.logging_config import get_logger
# logger = get_logger(__name__)

def get_logger(name: str = "ai_data_prep") -> logging.Logger:
    """إرجاع logger بالاسم المطلوب (child logger)"""
    return logging.getLogger(name)
