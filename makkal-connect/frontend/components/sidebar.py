import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.translations import t

def render_sidebar():
    # Force display stSidebar and stSidebarCollapsedControl on dashboard pages to override persistent landing page style tags
    st.markdown("<style>[data-testid='stSidebar'] { display: flex !important; } [data-testid='stSidebarCollapsedControl'] { display: flex !important; }</style>", unsafe_allow_html=True)
    st.sidebar.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 25px; padding-top: 15px;">
                <div style="font-size: 55px; filter: drop-shadow(0 4px 8px rgba(190, 18, 60, 0.1));">🏛️</div>
                <p style="color: #0F172A; font-size: 26px; font-weight: 800; margin-top: 10px; letter-spacing: -0.02em; background: linear-gradient(135deg, #0F172A 50%, var(--primary) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{t('Makkal Connect')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Language Toggle
    if "lang" not in st.session_state:
        st.session_state["lang"] = "EN"
        
    lang = st.sidebar.radio("Language / மொழி", ["English", "தமிழ்"], index=0 if st.session_state["lang"] == "EN" else 1)
    if lang == "English":
        if st.session_state["lang"] != "EN":
            st.session_state["lang"] = "EN"
            st.rerun()
    else:
        if st.session_state["lang"] != "TA":
            st.session_state["lang"] = "TA"
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.page_link("Home.py", label=t("Home"), icon="🏠")
    st.sidebar.page_link("pages/1_Citizen_Dashboard.py", label=t("Citizen Dashboard"), icon="🏛️")
    st.sidebar.page_link("pages/2_Volunteer_Dashboard.py", label=t("Volunteer Dashboard"), icon="👥")
    st.sidebar.page_link("pages/3_Councillor_Dashboard.py", label=t("Councillor Dashboard"), icon="📊")
    st.sidebar.page_link("pages/4_Charity_Welfare.py", label=t("Charity & Welfare"), icon="❤️")
    
    st.sidebar.divider()
    if st.session_state.get("user_role"):
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state["access_token"] = None
            st.session_state["view"] = "landing"
            st.session_state["user_role"] = None
            if "access_token" in st.session_state:
                del st.session_state["access_token"]
            st.rerun()
            
        role_upper = str(st.session_state.get("user_role")).upper()
        st.sidebar.markdown(
            f"""
            <div style="text-align: center; margin-top: 20px; padding: 16px; background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E8F0; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
                <p style="color: #64748B; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 6px 0;">{t('Logged in as')}</p>
                <p style="color: var(--primary); font-size: 16px; font-weight: 800; margin: 0; letter-spacing: 0.02em;">👤 {t(role_upper)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
