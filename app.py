import streamlit as st
import requests
import pandas as pd
import PyPDF2
import re

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="Enterprise AI Hiring", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #0f62fe, #8a3ffc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 900;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-text {
        font-size: 1.2rem;
        color: #555555;
        margin-top: 0px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="gradient-text">Explainable Hiring System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Context-Aware, EEOC-Compliant AI Recruitment Dashboard</p>', unsafe_allow_html=True)
st.divider()

# ==========================================
# 1. NLP RESUME PARSER ENGINE
# ==========================================
def parse_resume(file, all_certs, job_role):
    pdf_reader = PyPDF2.PdfReader(file)
    text = "".join(page.extract_text() or "" for page in pdf_reader.pages).lower()
    
    # Extract Experience
    exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', text)
    extracted_exp = min(int(exp_match.group(1)) if exp_match else 0, 20)
    
    # Extract Certifications
    found_certs = [cert for cert in all_certs if cert.split()[0].lower() in text]
             
    # Extract JD Match Score
    tech_keywords = ["python", "java", "sql", "aws", "cloud", "api", "react", "data", "agile", "leadership", "ml", "ai"]
    match_score = min(30 + sum(5 for word in tech_keywords + job_role.lower().split() if word in text), 100)
    
    return extracted_exp, found_certs, match_score

# ==========================================
# 2. UNBIASED DYNAMIC JOB CONTEXT
# ==========================================
def get_dynamic_certs(role_name):
    if not role_name: 
        return [], []
    
    role = role_name.lower()
    
    if any(x in role for x in ["machine learning", "ai", "artificial intelligence"]): 
        core = ["AWS ML Specialty", "Certified AI Professional (CAIP)", "TensorFlow Developer", "Google Cloud ML Engineer", "Azure AI Engineer", "DeepLearning.AI Spec."]
    elif "cloud" in role: 
        core = ["AWS Solutions Architect", "Google Cloud Architect", "Azure Administrator", "CompTIA Cloud+", "Cloud Security Professional (CCSP)", "AWS SysOps"]
    elif any(x in role for x in ["web", "developer", "software", "full stack"]): 
        core = ["Meta React Developer", "AWS Cloud Practitioner", "Node.js Certified", "MongoDB Developer", "Oracle Java Programmer", "CKA Kubernetes"]
    elif "data" in role: 
        core = ["Google Data Engineer", "Certified Data Professional (CDP)", "Databricks Certified", "Snowflake SnowPro", "Power BI Analyst", "Tableau Specialist"]
    else: 
        core = [f"{role_name.title()} Foundation", f"{role_name.title()} Practitioner", f"Advanced {role_name.title()}", f"Master {role_name.title()} Specialist", f"Enterprise {role_name.title()}", f"Lead {role_name.title()}"]
    
    bonus = ["Certified ScrumMaster (CSM)", "PMP Certification", "Six Sigma Green Belt", "ITIL 4 Foundation"]
    return core, bonus

# ==========================================
# 3. SIDEBAR: TARGET ROLE & UPLOAD
# ==========================================
st.sidebar.header("🎯 1. Target Role & Context")
job_role = st.sidebar.text_input("Search or Type Job Role", value="Machine Learning Engineer")
core_certs, bonus_certs = get_dynamic_certs(job_role)
all_possible_certs = core_certs + bonus_certs

if core_certs:
    st.sidebar.caption(f"**Core Requirements for {job_role}:**")
    for cert in core_certs[:3]: 
        st.sidebar.markdown(f"- {cert}")
st.sidebar.divider()

st.sidebar.header("📄 2. Upload Resume (Optional)")
uploaded_file = st.sidebar.file_uploader("Upload PDF to auto-fill metrics", type=["pdf"])

# Default Values
def_exp = 4
def_score = 65
def_certs = []

if uploaded_file and job_role:
    with st.spinner("Parsing document..."):
        def_exp, def_certs, def_score = parse_resume(uploaded_file, all_possible_certs, job_role)
    st.sidebar.success(f"ATS extracted data from {uploaded_file.name}")
st.sidebar.divider()

# ==========================================
# 4. SIDEBAR: CANDIDATE PROFILE & CERTS
# ==========================================
st.sidebar.header("👤 3. Candidate Profile")

# NEW FEATURE: The optional LinkedIn URL input
linkedin_url = st.sidebar.text_input("LinkedIn Profile (Optional)", placeholder="https://linkedin.com/in/...")

is_locked = uploaded_file is not None

# Experience is UNLOCKED so humans can fix parser mistakes
experience = st.sidebar.slider("Years of Relevant Experience", 0, 20, def_exp)

# JD Match is LOCKED to prevent tampering with the AI's math
tech_score = st.sidebar.slider("JD Skill Match (%)", 0, 100, def_score, disabled=is_locked)

st.sidebar.markdown("**Verified Credentials**")
if all_possible_certs:
    held_certs = st.sidebar.multiselect(
        "Select matching credentials", 
        all_possible_certs, 
        default=def_certs,
        help="Select any recognized industry credentials."
    )
    
    custom_certs_input = st.sidebar.text_input(
        "Add Unlisted Credentials", 
        placeholder="e.g. Cisco CCNA, Oracle DBA",
        help="Type any certifications not in the list above, separated by commas."
    )
    
    if custom_certs_input.strip():
        custom_certs_list = [c.strip() for c in custom_certs_input.split(",") if c.strip()]
    else:
        custom_certs_list = []
        
    total_held_certs = held_certs + custom_certs_list
    certs_count = min(len(total_held_certs), 10)
    
else: 
    certs_count = 0
    total_held_certs = []
    core_certs = []

st.sidebar.divider()
analyze_btn = st.sidebar.button("Run AI Analysis", type="primary", use_container_width=True)

# ==========================================
# 5. MAIN DASHBOARD AREA
# ==========================================
if analyze_btn and job_role:
    api_url = "http://127.0.0.1:8000/analyze_candidate"
    
    payload = {
        "experience_years": experience, 
        "technical_score": tech_score, 
        "certifications": certs_count
    }
    
    with st.spinner(f"Evaluating candidate for {job_role} role..."):
        try:
            response = requests.post(api_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                shap = result.get("shap_explanation", {})
                
                tab1, tab2 = st.tabs(["👔 Recruiter Audit View", "📩 Candidate Action Plan"])
                
                with tab1:
                    st.subheader(f"Evaluation for: {job_role}")
                    
                    # NEW FEATURE: Displaying the LinkedIn link if provided
                    if linkedin_url:
                        st.markdown(f"[🔗 View Candidate LinkedIn Profile]({linkedin_url})")
                        st.write("") # Adds a tiny bit of spacing
                    
                    if result.get("hired") == 1:
                        st.success(f"✅ **SHORTLIST APPROVED** - Candidate profile aligns with {job_role} requirements.")
                    else:
                        st.error(f"❌ **REJECTED** - Candidate falls below the threshold for the {job_role} position.")
                        
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Experience Matrix", f"{experience} Yrs", f"{shap.get('experience_years', 0)} pts")
                    col2.metric("JD Match Matrix", f"{tech_score}% Match", f"{shap.get('technical_score', 0)} pts")
                    col3.metric("Credential Matrix", f"{certs_count}/10 Certs", f"{shap.get('certifications', 0)} pts")
                    
                    st.divider()
                    st.markdown("**Mathematical Decision Audit (SHAP Visualized)**")
                    shap_df = pd.DataFrame({
                        "Feature": ["Experience", "JD Alignment", "Valid Certifications"],
                        "Impact": [shap.get("experience_years", 0), shap.get("technical_score", 0), shap.get("certifications", 0)]
                    }).set_index("Feature")
                    st.bar_chart(shap_df, color="#8a3ffc")
                    
                with tab2:
                    if result.get("hired") == 0:
                        st.error("🚨 **Candidacy Gap Analysis: Why Your Profile Was Flagged**")
                        
                        if shap.get('technical_score', 0) <= 0 or tech_score < 75:
                            st.markdown(f"- **Low Technical Alignment:** Your resume achieved only a **{tech_score}%** skill match with the Job Description (AI Penalty: {shap.get('technical_score', 0)} pts).")
                        
                        mandatory_missing = [c for c in core_certs[:3] if c not in total_held_certs]
                        if mandatory_missing:
                            st.markdown(f"- **Missing Core Credentials:** You are currently lacking strictly required certification(s): **{', '.join(mandatory_missing)}**.")
                        
                        if shap.get('experience_years', 0) < 0:
                            st.markdown(f"- **Insufficient Experience:** Your **{experience} years** of experience is below the competitive average for this seniority level (AI Penalty: {shap.get('experience_years', 0)} pts).")
                        else:
                            st.markdown(f"- ***Experience Note:*** Your **{experience} years** of experience was a positive factor (AI Boost: +{shap.get('experience_years', 0)} pts), but it could not outweigh the technical gaps.")
                            
                        st.divider()
                        st.info("🌱 **Actionable Growth Blueprint**")
                        
                        target_tech = max(85, tech_score + 15)
                        
                        step1, step2, step3 = st.columns(3)
                        with step1:
                            st.markdown("📚 **Phase 1: Upskill**")
                            st.markdown(f"Increase your technical alignment from **{tech_score}%** to at least **{target_tech}%**.")
                        with step2:
                            st.markdown("📜 **Phase 2: Certify**")
                            if mandatory_missing:
                                for c in mandatory_missing: st.markdown(f"- Obtain **{c}**")
                            else:
                                st.markdown("Acquire advanced or bonus certifications to strengthen your profile.")
                        with step3:
                            st.markdown("💼 **Phase 3: Apply**")
                            st.markdown(f"Re-apply in 6 months once technical milestones are reached.")
                            
                    else:
                        st.success(f"🎉 **Congratulations!** Your profile is highly competitive for the {job_role} position. Our recruitment team will be in touch shortly.")
                        st.balloons()
            
            else:
                st.error(f"🚨 **Backend API Error (Status Code: {response.status_code})**")
                st.warning("The AI Brain rejected the data payload. Here is the exact error:")
                st.code(response.text)
                
        except Exception as e:
            st.error("🚨 **Connection Error: Could not connect to the API!**")
            st.warning("Make sure your FastAPI server is running in a separate terminal using `python -m uvicorn main:app --reload`")
            
elif analyze_btn and not job_role:
    st.error("Please enter a Target Role before running the analysis.")
else:
    st.info("👈 Upload a resume OR adjust the profile manually in the sidebar, then click **Run AI Analysis**.")