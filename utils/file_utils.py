# utils/file_utils.py
import os
import re
from pathlib import Path

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 100

def is_allowed_file(filename: str) -> bool:
    """التحقق من أن امتداد الملف مسموح به"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def check_file_size(file_obj, max_mb: int = MAX_FILE_SIZE_MB) -> tuple:
    """
    التحقق من حجم الملف.
    يُرجع (is_ok, message)
    """
    try:
        file_obj.seek(0, 2)  # الانتقال لنهاية الملف
        size_bytes = file_obj.tell()
        file_obj.seek(0)     # إعادة المؤشر للبداية
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > max_mb:
            return False, f"حجم الملف ({size_mb:.1f} MB) يتجاوز الحد المسموح ({max_mb} MB)"
        return True, f"حجم الملف: {size_mb:.2f} MB"
    except Exception as e:
        return True, ""  # إذا فشل الفحص، نسمح بالملف

def sanitize_filename(filename: str) -> str:
    """تنظيف اسم الملف من الأحرف غير المسموحة"""
    name = Path(filename).stem
    ext = Path(filename).suffix
    name = re.sub(r'[^\w\-_\. ]', '_', name)
    name = name.strip('. ')
    return f"{name}{ext}" if name else f"file{ext}"

def get_file_extension(filename: str) -> str:
    """إرجاع امتداد الملف بأحرف صغيرة"""
    return Path(filename).suffix.lower()

def format_file_size(size_bytes: int) -> str:
    """تحويل الحجم بالبايت إلى نص مقروء"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    return f"{size_bytes / 1024 ** 3:.1f} GB"
