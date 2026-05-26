import streamlit as st
import pandas as pd
import plotly.express as px
from components.api_client import get, post, patch
from components.sidebar import render_sidebar
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.translations import t

st.set_page_config(page_title="Councillor Portal", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
render_sidebar()

role = st.session_state.get("user_role", "public")

st.title(f"📊 {t('Councillor Dashboard')}")

if role in ["public", "volunteer", "admin"]:
    # ---------------------------------------------------------
    # PUBLIC / LEADERSHIP / TRANSPARENCY VIEW
    # ---------------------------------------------------------
    st.subheader(t("Councillor Transparency & Performance"))
    
    tabs = st.tabs([t(x) for x in ["Performance Leaderboard", "Makkal Scorecard", "Work Completion Status", "Ward Updates"]])
    
    with tabs[0]:
        st.markdown(f"### {t('Councillor Performance Comparison')}")
        perf_data = pd.DataFrame([
            {"Councillor": "V. S. Mani", "Ward": "Ward 42", "Completion %": 92, "Complaints": 45, "Makkal Score": 4.8},
            {"Councillor": "K. Ravi", "Ward": "Ward 17", "Completion %": 85, "Complaints": 30, "Makkal Score": 4.5},
            {"Councillor": "M. Priya", "Ward": "Ward 8", "Completion %": 78, "Complaints": 60, "Makkal Score": 3.9},
            {"Councillor": "A. Kumar", "Ward": "Ward 104", "Completion %": 65, "Complaints": 20, "Makkal Score": 3.2},
        ])
        st.dataframe(perf_data.sort_values(by="Completion %", ascending=False), use_container_width=True)
        st.button("📄 Export Leadership Report (PDF)")

    with tabs[1]:
        st.markdown("### ⭐ Makkal Score (Citizen Ratings)")
        selected_councillor = st.selectbox("Select Councillor to View Detailed Ratings", perf_data["Councillor"])
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            #### {selected_councillor}'s Scorecard
            - **Responsiveness:** ⭐⭐⭐⭐⭐ (5/5)
            - **Work Quality:** ⭐⭐⭐⭐☆ (4/5)
            - **Availability:** ⭐⭐⭐☆☆ (3/5)
            - **Transparency:** ⭐⭐⭐⭐⭐ (5/5)
            - **Engagement:** ⭐⭐⭐⭐☆ (4/5)
            """)
        with c2:
            st.info("💡 **Makkal Score Calculation:** Based on 5-star citizen ratings across 5 key governance pillars.")

    with tabs[2]:
        st.markdown("### 🛠️ Public Work Completion Status")
        # Same logic as Citizen Dashboard but focused on councillor performance
        st.write("Tracking transparency on promises vs. completed tasks.")
        st.progress(85, text="85% of promised works completed this quarter")

    with tabs[3]:
        st.markdown("### 📍 Area-wise Development Updates")
        st.write("Live updates on infrastructure projects across wards.")
        st.success("✅ Ward 42: New Park Construction Completed")
        st.warning("⏳ Ward 17: Bus Shelter Work in Progress")

elif role == "councillor":
    # ---------------------------------------------------------
    # COUNCILLOR MANAGEMENT / CRUD VIEW
    # ---------------------------------------------------------
    st.subheader("🛠️ Councillor Management Portal (Back-office)")
    
    # Query real-time database records
    districts = get("/works/districts") or []
    wards = get("/works/wards") or []
    orders = get("/works/orders") or []
    complaints = get("/works/complaints") or []
    volunteers = get("/volunteers/") or []
    
    ward_to_district = {w["id"]: w["district_id"] for w in wards}
    ward_to_num = {w["id"]: w["ward_number"] for w in wards}
    district_options = {d["name"]: d["id"] for d in districts}
    ward_options = {w["ward_number"]: w["id"] for w in wards}
    
    tabs = st.tabs(["Work Order Mgmt", "AI Triage & Verification", "Volunteer Approvals", "Manifesto Tracker", "Team & War Room"])
    
    with tabs[0]:
        st.markdown("### 📝 Create / Update Work Orders")
        
        mode = st.radio("Mode", ["Create New Work Order", "Update Existing Work Order"], horizontal=True)
        
        if mode == "Create New Work Order":
            with st.form("create_work_order_form"):
                title = st.text_input("Work Title", placeholder="e.g. Repair drainage pipes in Anna Nagar")
                cat = st.selectbox("Category", ["Roads", "Drainage", "Water", "Electricity", "Sanitation"])
                
                # Fetch Wards
                ward_num_list = list(ward_options.keys()) if ward_options else ["W1"]
                selected_ward = st.selectbox("Target Ward", ward_num_list)
                
                budget = st.number_input("Sanctioned Budget (₹)", min_value=0.0, step=10000.0, value=250000.0)
                responsibility = st.text_input("Responsibility / Assigned Department", value="Public Works Department (PWD)")
                
                if st.form_submit_button("Submit Work Order"):
                    if not title.strip():
                        st.error("Work Title is required!")
                    else:
                        payload = {
                            "title": title,
                            "category": cat,
                            "ward_id": ward_options[selected_ward] if ward_options else 1,
                            "budget_sanctioned": budget,
                            "responsibility": responsibility,
                            "status": "Pending"
                        }
                        res = post("/works/orders", payload)
                        if res:
                            st.success(f"✅ Successfully created Work Order: '{title}'!")
                            st.rerun()
        else:
            if not orders:
                st.info("No work orders available in the database to update.")
            else:
                order_select_options = {f"{o['title']} ({ward_to_num.get(o['ward_id'], 'W1')})": o["id"] for o in orders}
                selected_order_label = st.selectbox("Select Work Order to Update", list(order_select_options.keys()))
                selected_order_id = order_select_options[selected_order_label]
                
                # Get selected order details
                order_obj = next((o for o in orders if o["id"] == selected_order_id), None)
                if order_obj:
                    with st.form("update_work_order_form"):
                        st.write(f"**Current Category:** {order_obj['category']}")
                        status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed", "Verified"], index=["Pending", "In Progress", "Completed", "Verified"].index(order_obj.get("status", "Pending")))
                        budget = st.number_input("Sanctioned Budget (₹)", min_value=0.0, step=10000.0, value=float(order_obj.get("budget_sanctioned", 0.0) or 0.0))
                        responsibility = st.text_input("Responsibility / Assigned Department", value=order_obj.get("responsibility", "Ward Councillor Office"))
                        
                        if st.form_submit_button("Update Work Order"):
                            payload = {
                                "status": status,
                                "budget_sanctioned": budget,
                                "responsibility": responsibility
                            }
                            res = patch(f"/works/orders/{selected_order_id}", payload)
                            if res:
                                st.success("✅ Successfully updated Work Order!")
                                st.rerun()
                                
    with tabs[1]:
        st.markdown("### 🤖 AI Triage & Complaint Verification")
        st.info("AI automatically triages incoming complaints. Verify them to convert into active public work orders.")
        
        pending_complaints = [c for c in complaints if c.get("status") not in ["Completed", "Verified"]]
        
        if not pending_complaints:
            st.success("🎉 All citizen complaints have been verified and processed!")
        else:
            for c in pending_complaints:
                priority = c.get("priority", "LOW").upper()
                priority_colors = {"LOW": "green", "MED": "orange", "HIGH": "red", "URGENT": "purple"}
                p_color = priority_colors.get(priority, "gray")
                
                with st.expander(f"⚙️ {c.get('category')} — Priority: {priority} (Filed at {c.get('location_address', 'Tamil Nadu')})"):
                    st.markdown(f"**AI Classification:** <span style='color:{p_color}; font-weight:bold;'>{priority} {c.get('category')}</span>", unsafe_allow_html=True)
                    st.write(f"**Citizen Description:** {c.get('description')}")
                    
                    if c.get("photo_url"):
                        st.image(c.get("photo_url"), caption="Complaint Photo Evidence", width=250)
                        
                    with st.form(f"verify_form_{c['id']}"):
                        ward_num_list = list(ward_options.keys()) if ward_options else ["W1"]
                        selected_ward = st.selectbox("Assign Target Ward", ward_num_list, key=f"ward_c_{c['id']}")
                        budget = st.number_input("Sanctioned Budget (₹)", min_value=0.0, step=10000.0, value=200000.0, key=f"budget_c_{c['id']}")
                        responsibility = st.text_input("Responsibility / Contractor in Charge", value="Highways Department", key=f"resp_c_{c['id']}")
                        
                        if st.form_submit_button("Verify & Approve Complaint"):
                            # 1. Create real work order
                            order_payload = {
                                "title": f"Approved: {c.get('category')} - {c.get('description')[:30]}...",
                                "category": c.get('category', 'Roads'),
                                "ward_id": ward_options[selected_ward] if ward_options else 1,
                                "budget_sanctioned": budget,
                                "responsibility": responsibility,
                                "status": "In Progress"
                            }
                            order_res = post("/works/orders", order_payload)
                            
                            # 2. Update complaint status in DB
                            res_verify = patch(f"/works/complaints/{c['id']}/verify?verify=true", {})
                            
                            st.success(f"✅ Complaint approved! Converted to Work Order: '{order_payload['title']}'!")
                            st.rerun()
                            
    with tabs[2]:
        st.markdown("### 🤝 Pending Volunteer Registrations")
        st.write("Approve newly registered Singapadai volunteers to activate their Digital ID card and QR code.")
        
        pending_volunteers = [v for v in volunteers if not v.get("is_approved", False)]
        
        if not pending_volunteers:
            st.success("🎉 No pending volunteer approvals! All registered volunteers are verified.")
        else:
            for v in pending_volunteers:
                with st.container():
                    st.markdown(f"""
                    <div style='padding: 15px; margin-bottom:15px; border-radius: 8px; border: 1px solid #D97706; background-color: rgba(217, 119, 6, 0.05);'>
                        <h4>👤 {v.get('full_name')}</h4>
                        <p>📞 Phone: {v.get('phone')} | ✉️ Email: {v.get('email', 'N/A')}</p>
                        <p>📍 District ID: {v.get('district_id')} | Ward/Block: {v.get('block', 'N/A')} | Booth: {v.get('booth_number', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Approve {v.get('full_name')}", key=f"app_vol_{v['id']}"):
                        res = patch(f"/volunteers/{v['id']}/approve", {})
                        if res:
                            st.success(f"✅ Successfully approved {v.get('full_name')}! Digital ID is now active.")
                            st.rerun()

    with tabs[3]:
        st.subheader("🤖 AI Manifesto Tracker")
        st.file_uploader("Upload Manifesto PDF to Track Promises", type="pdf")
        st.button("Run AI Analysis")

    with tabs[4]:
        st.subheader("🛡️ Team Management & Event War Room")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Activate War Room Mode"):
                st.error("War Room Activated! Live tracking volunteers...")
        with col2:
            st.text_area("WhatsApp Broadcast to Volunteers")
            st.button("Send Broadcast")

elif role == "admin":
    # ---------------------------------------------------------
    # ADMIN PORTAL
    # ---------------------------------------------------------
    st.subheader("🛡️ Administrator Master Management Portal")
    
    # Query database
    districts = get("/works/districts") or []
    wards = get("/works/wards") or []
    orders = get("/works/orders") or []
    complaints = get("/works/complaints") or []
    volunteers = get("/volunteers/") or []
    
    # Statistics cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card" style="text-align:center;"><h3>Total Work Orders</h3><h1>{len(orders)}</h1></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card" style="text-align:center;"><h3>Total Complaints Filed</h3><h1>{len(complaints)}</h1></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card" style="text-align:center;"><h3>Registered Volunteers</h3><h1>{len(volunteers)}</h1></div>', unsafe_allow_html=True)
    with c4:
        approved_vol = len([v for v in volunteers if v.get("is_approved")])
        st.markdown(f'<div class="metric-card" style="text-align:center;"><h3>Approved Volunteers</h3><h1 style="color:#10B981;">{approved_vol}</h1></div>', unsafe_allow_html=True)
        
    admin_tabs = st.tabs(["Master Work Orders List", "Master Complaints List", "Singapadai Volunteers Database"])
    
    with admin_tabs[0]:
        st.markdown("### 📋 System Master Work Orders")
        if orders:
            df_o = pd.DataFrame(orders)
            st.dataframe(df_o, use_container_width=True)
        else:
            st.info("No work orders in the database.")
            
    with admin_tabs[1]:
        st.markdown("### 🗣️ Master Complaints Registry")
        if complaints:
            df_c = pd.DataFrame(complaints)
            st.dataframe(df_c, use_container_width=True)
        else:
            st.info("No complaints lodged yet.")
            
    with admin_tabs[2]:
        st.markdown("### 👥 Singapadai Volunteers Database")
        if volunteers:
            df_v = pd.DataFrame(volunteers)
            st.dataframe(df_v, use_container_width=True)
        else:
            st.info("No volunteers registered yet.")

else:
    st.warning("Please log in to access this module.")
