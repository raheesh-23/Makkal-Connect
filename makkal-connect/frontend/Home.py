import streamlit as st
import requests
import os
import pandas as pd
from utils.translations import t

st.set_page_config(page_title="Makkal Connect", layout="wide")

# Initialize session state
if "view" not in st.session_state:
    st.session_state["view"] = "landing"
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            css_content = f.read()
            # Append conditional styles based on current view state
            if st.session_state.get("view", "landing") in ["landing", "login_volunteer", "login_councillor", "login_admin"]:
                css_content += "\n[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'] { display: none !important; }\n"
            else:
                css_content += "\n[data-testid='stSidebar'] { display: flex !important; }\n[data-testid='stSidebarCollapsedControl'] { display: flex !important; }\n"
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

load_css()



def show_landing():
    st.markdown(f"<h1 style='text-align: center; margin-top: 5vh; font-size: 3.2rem;'>{t('Makkal Connect')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #94A3B8; font-size: 20px; margin-bottom: 6vh; font-weight: 500;'>{t('Citizen Digital Governance Platform')}</p>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 45px; color: var(--accent); font-weight: 700;'>🎯 {t('Select Your Portal')}</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
            <div class="role-card">
                <div>
                    <div class="role-icon">👥</div>
                    <div class="role-title">{t('PUBLIC')}</div>
                    <div class="role-desc">No login required. Explore councillor metrics, view promises scorecard, and report civic issues directly.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t("Enter Public Portal"), key="btn_public", use_container_width=True):
            st.session_state["user_role"] = "public"
            st.session_state["view"] = "dashboard"
            st.rerun()
            
    with c2:
        st.markdown(f"""
            <div class="role-card">
                <div>
                    <div class="role-icon">🤝</div>
                    <div class="role-title">{t('VOLUNTEER')}</div>
                    <div class="role-desc">Singapadai portal. Verify with Aadhar, activate your digital QR ID card, and participate in emergency war rooms.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t("Aadhar Verification"), key="btn_vol", use_container_width=True):
            st.session_state["view"] = "login_volunteer"
            st.rerun()
            
    with c3:
        st.markdown(f"""
            <div class="role-card">
                <div>
                    <div class="role-icon">📊</div>
                    <div class="role-title">{t('COUNCILLOR')}</div>
                    <div class="role-desc">Official portal for ward representatives. Action AI complaints, manage local volunteer approvals, and update manifesto tracker.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t("Official Login"), key="btn_councillor", use_container_width=True):
            st.session_state["view"] = "login_councillor"
            st.rerun()

    with c4:
        st.markdown(f"""
            <div class="role-card">
                <div>
                    <div class="role-icon">🛡️</div>
                    <div class="role-title">{t('ADMIN')}</div>
                    <div class="role-desc">System administration and oversight. Audit district metrics, inspect registered users database, and audit public logs.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(t("Security Login"), key="btn_admin", use_container_width=True):
            st.session_state["view"] = "login_admin"
            st.rerun()

def show_login_volunteer():
    st.markdown(f"<h2 style='text-align: center;'>{t('Volunteer Verification')}</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='padding: 2rem; border-radius: 10px;'>", unsafe_allow_html=True)
        aadhar = st.text_input("Enter Aadhar Number", type="password")
        if st.button("Send OTP"):
            st.session_state["otp_sent"] = True
            st.success("OTP sent to linked mobile number: ******9876")
        
        if st.session_state.get("otp_sent"):
            otp = st.text_input("Enter OTP")
            if st.button("Verify & Enter"):
                if aadhar == "123456789" and otp == "987654321":
                    st.session_state["user_role"] = "volunteer"
                    st.session_state["view"] = "dashboard"
                    st.rerun()
                elif len(aadhar) == 12 and len(otp) == 6:
                    # Keep existing logic for standard lengths if needed, 
                    # but prioritize user's requested dummy credentials
                    st.session_state["user_role"] = "volunteer"
                    st.session_state["view"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid Aadhar or OTP. Hint: Use the demo credentials.")
        
        if st.button("← Back"):
            st.session_state["view"] = "landing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def show_login_councillor():
    st.markdown(f"<h2 style='text-align: center;'>{t('Councillor Portal')}</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='padding: 2rem; border-radius: 10px;'>", unsafe_allow_html=True)
        name = st.text_input("Full Name")
        ward = st.text_input("Ward Number")
        party = st.text_input("Party Name")
        if st.button("Verify Credentials"):
            if name and ward and party:
                res = requests.post("http://api:8000/api/v1/auth/login", data={"username": "councillor@tvk.com", "password": "councillor123"})
                if res.status_code == 200:
                    st.session_state["access_token"] = res.json()["access_token"]
                    st.session_state["user_role"] = "councillor"
                    st.session_state["view"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Failed to authenticate with backend API")
            else:
                st.warning("Please fill all fields")
        
        if st.button("← Back"):
            st.session_state["view"] = "landing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def show_login_admin():
    st.markdown(f"<h2 style='text-align: center;'>{t('Admin Login')}</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='padding: 2rem; border-radius: 10px;'>", unsafe_allow_html=True)
        email = st.text_input(t("Email"))
        password = st.text_input(t("Password"), type="password")
        if st.button(t("Login")):
            res = requests.post("http://api:8000/api/v1/auth/login", data={"username": email, "password": password})
            if res.status_code == 200:
                st.session_state["access_token"] = res.json()["access_token"]
                st.session_state["user_role"] = "admin"
                st.session_state["view"] = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        if st.button("← Back"):
            st.session_state["view"] = "landing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Main Application Logic
if st.session_state["view"] == "landing":
    show_landing()
elif st.session_state["view"] == "login_volunteer":
    show_login_volunteer()
elif st.session_state["view"] == "login_councillor":
    show_login_councillor()
elif st.session_state["view"] == "login_admin":
    show_login_admin()
else:
    from components.sidebar import render_sidebar
    render_sidebar()
    st.markdown(f"<h1 style='color: #991B1B;'>{t('Dashboard')}</h1>", unsafe_allow_html=True)
    st.success(f"Welcome to Makkal Connect! You are logged in as: **{st.session_state['user_role'].upper()}**")
    st.info(t("Select a module from the sidebar to begin."))

