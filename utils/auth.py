# utils/auth.py
import streamlit as st
from utils.user_manager import verify_user, register_user, reset_password, load_users

def check_password():
    if st.session_state.get("authenticated", False):
        return True

    st.title("🔐 Welcome to AI Data Prep")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                success, msg = verify_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"Welcome {username}!")
                    st.rerun()
                else:
                    st.error(msg)
        with col2:
            if st.button("Forgot Password?"):
                st.info("Contact admin to reset password or create a new account.")
    
    with tab2:
        new_username = st.text_input("Choose Username", key="reg_username")
        new_password = st.text_input("Choose Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Create Account"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 4:
                st.error("Password must be at least 4 characters")
            else:
                success, msg = register_user(new_username, new_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    
    return False

def logout():
    """تسجيل الخروج: مسح حالة المصادقة وإعادة التوجيه لشاشة الدخول"""
    for key in ["authenticated", "username"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def change_password(username, old_password, new_password, confirm_new):
    """تغيير كلمة المرور للمستخدم المسجل دخوله"""
    if new_password != confirm_new:
        return False, "New passwords do not match"
    if len(new_password) < 4:
        return False, "Password must be at least 4 characters"
    # التحقق من صحة كلمة المرور القديمة
    success, _ = verify_user(username, old_password)
    if not success:
        return False, "Old password is incorrect"
    # تحديث كلمة المرور
    return reset_password(username, new_password)