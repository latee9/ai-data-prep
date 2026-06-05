# connectors/api_connector.py
import streamlit as st
import pandas as pd
import requests
from typing import Optional


def fetch_api_data(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    body: Optional[dict] = None,
    data_path: str = "",
    timeout: int = 30,
) -> Optional[pd.DataFrame]:
    """
    جلب بيانات من REST API وتحويلها إلى DataFrame.

    Args:
        url: رابط الـ API
        method: GET أو POST
        headers: ترويسات الطلب (مثل Authorization)
        params: معاملات الـ query string
        body: جسم الطلب (POST فقط)
        data_path: المسار داخل JSON للوصول للبيانات (مثل "data.results")
        timeout: مهلة الاتصال بالثواني
    """
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers or {},
            params=params or {},
            json=body if method.upper() == "POST" else None,
            timeout=timeout,
        )
        response.raise_for_status()
        json_data = response.json()

        # التنقل عبر المسار المحدد
        if data_path:
            for key in data_path.split("."):
                if isinstance(json_data, dict) and key in json_data:
                    json_data = json_data[key]
                else:
                    st.error(f"المسار '{data_path}' غير موجود في الاستجابة")
                    return None

        # تحويل للـ DataFrame
        if isinstance(json_data, list):
            return pd.DataFrame(json_data)
        elif isinstance(json_data, dict):
            return pd.DataFrame([json_data])
        else:
            st.error("تنسيق الاستجابة غير مدعوم (يجب أن يكون JSON array أو object)")
            return None

    except requests.exceptions.ConnectionError:
        st.error(f"تعذّر الاتصال بـ: {url}")
    except requests.exceptions.Timeout:
        st.error(f"انتهت مهلة الاتصال ({timeout} ثانية)")
    except requests.exceptions.HTTPError as e:
        st.error(f"خطأ HTTP {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        st.error(f"خطأ غير متوقع: {e}")
    return None


def render_api_ui() -> Optional[pd.DataFrame]:
    """واجهة Streamlit لتكوين واستدعاء REST API"""
    st.subheader("🌐 استيراد بيانات من REST API")

    url = st.text_input("رابط الـ API", placeholder="https://api.example.com/data")
    method = st.radio("طريقة الطلب", ["GET", "POST"], horizontal=True)

    with st.expander("⚙️ خيارات متقدمة", expanded=False):
        auth_type = st.selectbox("نوع المصادقة", ["بدون", "Bearer Token", "API Key Header"])
        token = ""
        if auth_type == "Bearer Token":
            token = st.text_input("Bearer Token", type="password")
        elif auth_type == "API Key Header":
            api_key_name = st.text_input("اسم الـ Header", value="X-API-Key")
            token = st.text_input("قيمة الـ API Key", type="password")

        data_path = st.text_input(
            "مسار البيانات في JSON",
            placeholder="مثال: data.results (اتركه فارغاً إذا كانت البيانات في الجذر)"
        )

        if method == "POST":
            import json
            body_text = st.text_area("جسم الطلب (JSON)", "{}", height=100)
            try:
                body = json.loads(body_text)
            except Exception:
                st.error("JSON غير صالح في جسم الطلب")
                body = {}
        else:
            body = None

    if st.button("📡 جلب البيانات", disabled=not url):
        headers = {}
        if auth_type == "Bearer Token" and token:
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "API Key Header" and token:
            headers[api_key_name] = token

        with st.spinner("جاري الاتصال..."):
            df = fetch_api_data(
                url=url,
                method=method,
                headers=headers,
                data_path=data_path,
                body=body,
            )
            if df is not None:
                st.success(f"✅ تم جلب {len(df):,} صف و {df.shape[1]} عمود")
                return df
    return None
