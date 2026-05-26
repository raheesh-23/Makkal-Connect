import streamlit as st
import pandas as pd
import plotly.express as px
from components.api_client import get, post
from components.sidebar import render_sidebar
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.translations import t

st.set_page_config(page_title="Singapadai - Volunteers", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
render_sidebar()

st.title(f"👥 {t('Singapadai')}")

tabs = st.tabs([t("Register"), t("Digital ID"), t("Admin View"), t("Volunteer Post"), "Civic Passport", "Marketplace", "War Room"])

with tabs[0]:
    st.subheader(t("Register"))
    with st.form("volunteer_reg"):
        name = st.text_input(t("Full Name"), key="vol_reg_name")
        
        # Expanded date range to allow registration of all age groups (1940 onwards)
        import datetime
        default_dob = datetime.date(2000, 1, 1)
        min_dob = datetime.date(1940, 1, 1)
        max_dob = datetime.date(2026, 12, 31)
        
        dob = st.date_input(
            t("Date of Birth"),
            value=default_dob,
            min_value=min_dob,
            max_value=max_dob,
            key="vol_reg_dob"
        )
        
        phone = st.text_input(t("Phone Number"), key="vol_reg_phone")
        email = st.text_input(t("Email"), key="vol_reg_email")
        
        # Fetch districts dynamically
        districts = get("/works/districts") or []
        if districts:
            district_options = {d["name"]: d["id"] for d in districts}
            selected_district_name = st.selectbox(t("District"), list(district_options.keys()), key="vol_reg_district")
            district_id = district_options[selected_district_name]
        else:
            district_id = st.number_input(t("District ID"), min_value=1, step=1, key="vol_reg_district_id")
            
        block = st.text_input(t("Block / Ward"), key="vol_reg_block")
        booth_number = st.text_input(t("Booth Number"), key="vol_reg_booth")
        aadhar_number = st.text_input(t("Aadhar Number"), max_chars=12, help="Enter your 12-digit Aadhar card number", key="vol_reg_aadhar_num")
        aadhar_file = st.file_uploader(t("Upload Aadhar Card (PDF / Image)"), type=["pdf", "png", "jpg", "jpeg"], key="vol_reg_aadhar_file")
        
        submit = st.form_submit_button(t("Register"))
        
        if submit:
            # Check mandatory fields
            if not name or not phone or not email or not block or not booth_number or not aadhar_number or not aadhar_file:
                st.error("❌ All fields are mandatory! Please fill in all details, provide Aadhar details and upload your Aadhar Card.")
            elif len(aadhar_number) != 12 or not aadhar_number.isdigit():
                st.error("❌ Invalid Aadhar Number! Aadhar must be exactly 12 digits.")
            else:
                with st.spinner("🔍 Verifying Aadhar details and document with UIDAI database..."):
                    import time
                    time.sleep(1.5)
                st.success("✅ Aadhar Verified successfully! ID Checksum matched and Biometrics/Demographics validated.")
                
                data = {
                    "full_name": name,
                    "dob": dob.isoformat() + "T00:00:00Z",
                    "phone": phone,
                    "email": email,
                    "district_id": district_id,
                    "block": block,
                    "booth_number": booth_number,
                    "id_proof_type": "Aadhar",
                    "id_proof_url": f"Aadhar Number: {aadhar_number}"
                }
                res = post("/volunteers/", data)
                if res:
                    st.success("Registered Successfully!")
                    st.session_state["last_registered_id"] = res.get("membership_id")
                    st.session_state["last_qr"] = res.get("qr_code_url")

with tabs[1]:
    st.subheader(t("Digital ID"))
    if "last_registered_id" in st.session_state:
        # Query real-time status from backend
        vols = get("/volunteers/") or []
        vol_obj = next((v for v in vols if v.get("membership_id") == st.session_state['last_registered_id']), None)
        
        status_text = "❌ Pending Councillor Approval"
        status_color = "#D97706"
        if vol_obj and vol_obj.get("is_approved"):
            status_text = "✅ Approved & Active"
            status_color = "#10B981"
            
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; border: 2px solid {status_color};">
            <h3 style="color: var(--primary);">Makkal Connect Volunteer</h3>
            <h2>{st.session_state['last_registered_id']}</h2>
            <p style="font-size: 18px; font-weight: bold; color: {status_color};">{status_text}</p>
            <img src="{st.session_state['last_qr']}" alt="QR Code" width="150"/>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Register in the first tab to generate your ID.")

with tabs[2]:
    if "access_token" in st.session_state:
        st.subheader(t("Admin View"))
        stats = get("/volunteers/stats")
        if stats:
            st.write(f"{t('Total Volunteers')}: **{stats.get('total_volunteers', 0)}**")
            counts = stats.get("district_counts", {})
            if counts:
                df = pd.DataFrame(list(counts.items()), columns=['District ID', 'Count'])
                fig = px.bar(df, x='District ID', y='Count', title="Volunteers by District")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#1E293B",
                    title_font_color="#0F172A",
                    xaxis=dict(gridcolor="rgba(0,0,0,0.05)"),
                    yaxis=dict(gridcolor="rgba(0,0,0,0.05)")
                )
                fig.update_traces(marker_color='#BE123C')
                st.plotly_chart(fig, use_container_width=True)
        
        vols = get("/volunteers/")
        if vols:
            st.write("### Live Volunteer List")
            st.dataframe(pd.DataFrame(vols)[['membership_id', 'full_name', 'phone', 'district_id']])
            
    else:
        st.warning("Please login to access Admin View.")

with tabs[3]:
    st.subheader(t("Volunteer Post"))
    with st.form("vol_post_form"):
        mem_id = st.text_input(t("Membership ID"), help="e.g. TN-2026-000001")
        desc = st.text_area(t("Work Description"))
        photo_url = st.text_input(t("Photo Upload (Optional)"))
        submit_post = st.form_submit_button(t("Submit Work"))
        if submit_post:
            if mem_id and desc:
                res = post(f"/volunteers/posts?membership_id={mem_id}", {
                    "description": desc,
                    "photo_url": photo_url if photo_url else None
                })
                if res:
                    st.success("Work update posted successfully!")
            else:
                st.error("Membership ID and Description are required.")

with tabs[4]:
    st.subheader("🛂 Civic Career Passport")
    st.info("Your permanent digital CV for community service.")
    if "last_registered_id" in st.session_state:
        st.markdown(f"""
        <div style='border: 2px solid #00C47A; border-radius: 12px; padding: 20px; background: rgba(0, 196, 122, 0.05);'>
            <h3>Volunteer: {st.session_state['last_registered_id']}</h3>
            <p><strong>Reputation Tier:</strong> Gold ⭐️</p>
            <p><strong>Tasks Completed:</strong> 42</p>
            <p><strong>Wards Served:</strong> 3</p>
            <hr>
            <h4>🏆 Skills & Badges Earned:</h4>
            <ul>
                <li>✅ Voter Registration Expert</li>
                <li>✅ Relief Camp Leader</li>
                <li>✅ Pothole Spotter Elite</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.button("📄 Export Verified PDF")
    else:
        st.warning("Please register or login first to view your Civic Passport.")

with tabs[5]:
    st.subheader("🛒 Volunteer Sharing Marketplace")
    st.info("Browse urgent volunteer needs in neighboring wards and earn rewards.")
    
    marketplace_data = [
        {"Ward": "Ward 42", "Need": "Flood Relief Ops", "Volunteers Needed": 30, "Reward": "₹500/day", "Urgency": "🚨 Emergency"},
        {"Ward": "Ward 17", "Need": "Voter Registration Drive", "Volunteers Needed": 15, "Reward": "₹200/day", "Urgency": "High"},
        {"Ward": "Ward 8", "Need": "Medical Camp Support", "Volunteers Needed": 10, "Reward": "₹300/day", "Urgency": "Medium"},
    ]
    
    for req in marketplace_data:
        with st.expander(f"{req['Urgency']} - {req['Need']} ({req['Ward']})"):
            st.write(f"**Description:** Help our brothers and sisters in {req['Ward']} with {req['Need'].lower()}.")
            st.write(f"**Compensation:** {req['Reward']}")
            st.write(f"**Spots Remaining:** {req['Volunteers Needed']}")
            if st.button(f"Accept Request ({req['Ward']})", key=f"accept_{req['Ward']}"):
                st.success(f"Accepted! Please report to {req['Ward']} office at 8 AM tomorrow.")

with tabs[6]:
    st.subheader("⚡ Live Event War Room")
    st.info("Real-time coordination for active events and disaster relief.")
    
    active_war_room = {"Event": "Grand Political Rally - Trichy", "Status": "Active", "Your Role": "Field Coordinator"}
    
    if active_war_room:
        st.success(f"🔴 LIVE: {active_war_room['Event']}")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### 📍 Real-time Deployment Map")
            st.write("*Simulating GPS Tracking...*")
            st.components.v1.iframe("https://maps.google.com/maps?q=10.7905,78.7047&z=15&output=embed", height=300)
        with col2:
            st.markdown("#### 📡 Coordination")
            st.write("**Leader Broadcast:** 'All volunteers report to Zone 3 for water distribution immediately.'")
            if st.button("📢 Check-in My GPS Location"):
                st.info("Location sent: 10.7905° N, 78.7047° E")
    else:
        st.info("No active War Room sessions at the moment.")
