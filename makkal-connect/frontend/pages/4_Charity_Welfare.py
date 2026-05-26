import streamlit as st
import pandas as pd
from components.api_client import get, post
from components.sidebar import render_sidebar
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.translations import t

st.set_page_config(page_title="Charity & Welfare", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
render_sidebar()

st.title(f"❤️ {t('Charity & Welfare')}")

tabs = st.tabs([t("Active Campaigns"), t("Blood Donor Network"), t("Welfare Requests")])

with tabs[0]:
    st.subheader(t("Active Campaigns"))
    campaigns = get("/charity/campaigns") or []
    
    if campaigns:
        cols = st.columns(3)
        for i, c in enumerate(campaigns):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{c.get('type_emoji', '')} {c.get('title', '')}</h3>
                    <p>Target: {c.get('target_beneficiaries', 0)}</p>
                    <p>Current: {c.get('current_beneficiaries', 0)}</p>
                    <progress value="{c.get('current_beneficiaries', 0)}" max="{c.get('target_beneficiaries', 1)}" style="width:100%"></progress>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No active campaigns.")

with tabs[1]:
    st.subheader(f"🩸 {t('Blood Donor Network')}")
    
    role = st.session_state.get("user_role")
    is_privileged = role in ["councillor", "admin"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔍 Search Donors")
        bg = st.selectbox(t("Search Blood Group"), ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        if st.button(t("Search Donors")):
            donors = get(f"/charity/donors?blood_group={bg.replace('+', '%2B')}")
            if donors:
                df = pd.DataFrame(donors)
                if is_privileged:
                    df_disp = df[['name', 'blood_group', 'phone']]
                    st.dataframe(df_disp, use_container_width=True)
                else:
                    df['masked_phone'] = df['phone'].apply(lambda x: f"******{str(x)[-4:]}" if len(str(x)) >= 4 else "******")
                    df_disp = df[['masked_name', 'blood_group', 'masked_phone']]
                    df_disp.columns = ['name', 'blood_group', 'phone']
                    st.dataframe(df_disp, use_container_width=True)
            else:
                st.info("No donors found for this blood group.")
                
    with col2:
        if not is_privileged:
            st.markdown(f"### 🤝 {t('Register as Blood Donor')}")
            with st.form("add_donor_form"):
                donor_name = st.text_input(t("Full Name"), placeholder="e.g. Anand Kumar")
                donor_bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                donor_phone = st.text_input(t("Phone Number"), placeholder="e.g. 9876543210")
                
                districts = get("/works/districts") or []
                district_options = {d["name"]: d["id"] for d in districts} if districts else {"Chennai": 1}
                donor_district = st.selectbox(t("Emergency District"), list(district_options.keys()))
                
                submitted = st.form_submit_button(t("Register"))
                if submitted:
                    if not donor_name or not donor_phone:
                        st.error("Name and Phone Number are required!")
                    else:
                        payload = {
                            "name": donor_name,
                            "blood_group": donor_bg,
                            "phone": donor_phone,
                            "district_id": district_options[donor_district]
                        }
                        res = post("/charity/donors", payload)
                        if res:
                            st.success("🎉 Thank you! You have been successfully registered as a TVK Blood Network Donor!")
                            st.rerun()
            
            st.markdown("---")
            st.markdown(f"### 🚨 {t('Trigger Emergency Alert')}")
            districts = get("/works/districts") or []
            if districts:
                district_options = {d["name"]: d["id"] for d in districts}
                selected_district_name = st.selectbox(t("Emergency District"), list(district_options.keys()), key="public_alert_district")
                dist_id = district_options[selected_district_name]
            else:
                dist_id = st.number_input(t("Emergency District ID"), min_value=1, step=1, key="public_alert_district_id")
            
            alert_bg = st.selectbox(t("Search Blood Group"), ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], key="public_alert_bg")
            if st.button(t("Trigger Emergency Alert SMS"), key="public_alert_btn"):
                res = post(f"/charity/donors/emergency?blood_group={alert_bg.replace('+', '%2B')}&district_id={dist_id}", {})
                if res:
                    st.success(res.get("message", "Alert triggered!"))
        else:
            st.markdown(f"### 📋 {t('Blood Donor Submissions')}")
            st.markdown(f"*{t('View Box containing all registered user submissions:')}*")
            
            all_donors = get("/charity/donors")
            if all_donors:
                df_all = pd.DataFrame(all_donors)
                df_disp = df_all[['name', 'blood_group', 'phone']]
                st.dataframe(df_disp, use_container_width=True)
            else:
                st.info("No blood donor submissions found.")
                
            st.markdown("---")
            st.markdown(f"### 🚨 {t('Emergency Response Deck')}")
            districts = get("/works/districts") or []
            if districts:
                district_options = {d["name"]: d["id"] for d in districts}
                selected_district_name = st.selectbox(t("Emergency District"), list(district_options.keys()), key="privileged_alert_district")
                dist_id = district_options[selected_district_name]
            else:
                dist_id = st.number_input(t("Emergency District ID"), min_value=1, step=1, key="privileged_alert_district_id")
                
            if st.button(t("Trigger Emergency Alert SMS"), key="privileged_alert_btn"):
                res = post(f"/charity/donors/emergency?blood_group={bg.replace('+', '%2B')}&district_id={dist_id}", {})
                if res:
                    st.success(res.get("message", "Alert triggered!"))

with tabs[2]:
    st.subheader(t("Welfare Requests"))
    if "access_token" in st.session_state:
        reqs = get("/charity/welfare") or []
        if reqs:
            st.dataframe(pd.DataFrame(reqs), width='stretch')
        else:
            st.info("No welfare requests found.")
    else:
        st.info("Please login to view welfare requests.")
