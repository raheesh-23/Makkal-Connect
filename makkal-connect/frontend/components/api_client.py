import os
import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://api:8000").rstrip("/") + "/api/v1"

def get_headers():
    headers = {"Content-Type": "application/json"}
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
    return headers

def get(endpoint: str, params: dict = None):
    try:
        res = requests.get(f"{API_URL}{endpoint}", headers=get_headers(), params=params)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API GET Error: {e}")
        return None

def post(endpoint: str, data: dict):
    try:
        res = requests.post(f"{API_URL}{endpoint}", headers=get_headers(), json=data)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API POST Error: {e}")
        return None

def patch(endpoint: str, data: dict):
    try:
        res = requests.patch(f"{API_URL}{endpoint}", headers=get_headers(), json=data)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API PATCH Error: {e}")
        return None
