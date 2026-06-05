# utils/user_manager.py
import json
import os
import hashlib
import secrets as secrets_lib

USERS_FILE = "users.json"

# ─── تشفير كلمات المرور ──────────────────────────────────────────────────────

def _hash_password(password: str, salt: str = None) -> tuple:
    if salt is None:
        salt = secrets_lib.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hashed, salt

def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    hashed, _ = _hash_password(password, salt)
    return hashed == stored_hash

# ─── Seed من Streamlit Secrets (للنشر السحابي) ──────────────────────────────

def _seed_from_secrets():
    """
    إذا لم يوجد users.json، يُنشئه من st.secrets تلقائياً.
    يدعم على Streamlit Cloud الإعداد:
      [admin]
      username = "admin"
      password = "YourPassword123"
    """
    try:
        import streamlit as st
        admin_cfg = st.secrets.get("admin", {})
        uname = admin_cfg.get("username", "admin")
        pw    = admin_cfg.get("password", "Admin@123")
        hashed, salt = _hash_password(pw)
        save_users({
            uname: {"password": hashed, "salt": salt, "needs_reset": False}
        })
    except Exception:
        # في بيئة محلية بدون secrets: إنشاء admin افتراضي
        hashed, salt = _hash_password("Admin@123")
        save_users({
            "admin": {"password": hashed, "salt": salt, "needs_reset": False}
        })

# ─── قراءة/حفظ المستخدمين ────────────────────────────────────────────────────

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        _seed_from_secrets()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ─── ترحيل كلمات المرور القديمة ──────────────────────────────────────────────

def migrate_plain_passwords():
    users = load_users()
    changed = False
    for username, data in users.items():
        if "salt" not in data:
            plain_pw = data.get("password", "")
            hashed, salt = _hash_password(plain_pw)
            users[username]["password"] = hashed
            users[username]["salt"] = salt
            changed = True
    if changed:
        save_users(users)

# ─── عمليات المستخدمين ────────────────────────────────────────────────────────

def register_user(username: str, password: str) -> tuple:
    if not username or not username.strip():
        return False, "Username cannot be empty"
    users = load_users()
    if username in users:
        return False, "Username already exists"
    hashed, salt = _hash_password(password)
    users[username] = {"password": hashed, "salt": salt, "needs_reset": False}
    save_users(users)
    return True, "User registered successfully"

def verify_user(username: str, password: str) -> tuple:
    users = load_users()
    if username not in users:
        return False, "Invalid username or password"
    data = users[username]
    if "salt" not in data:
        migrate_plain_passwords()
        users = load_users()
        data = users.get(username, {})
    if _verify_password(password, data["password"], data["salt"]):
        return True, ""
    return False, "Invalid username or password"

def reset_password(username: str, new_password: str) -> tuple:
    users = load_users()
    if username not in users:
        return False, "User not found"
    hashed, salt = _hash_password(new_password)
    users[username]["password"] = hashed
    users[username]["salt"] = salt
    users[username]["needs_reset"] = False
    save_users(users)
    return True, "Password reset successfully"

def set_needs_reset(username: str):
    users = load_users()
    if username in users:
        users[username]["needs_reset"] = True
        save_users(users)
