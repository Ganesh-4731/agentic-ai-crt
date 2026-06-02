import streamlit as str
import requests
from pypdf import PdfReader
import json

# Page Configuration
str.set_page_config(
    page_title="Talent Sync - AI Job Assistant",
    page_icon="🎯",
    layout="wide"
)

str.title("🎯 Talent Sync")
str.caption("Autonomous, Free-to-Run Job Application Assistant")

# Initialize Session State for Results
if "analysis_result" not in str.session_state:
    str.session_state.analysis_result = None

# Sidebar Configuration
with str.sidebar:
    str.header("Configuration")
    webhook_url = str.text_input(
        "n8n Webhook URL",
        value="http://localhost:5678/webhook-test/apply",
        help="Use the test URL for development, change to production URL later."
    )
    str.info("Ensure your local n8n instance is running (`n8n start`).")

# Layout Split
col1, col2 = str.columns([1, 1], gap="large")

with col1:
    str.subheader("Design Your Application")
    
    uploaded_file = str.file_uploader("Upload your Resume (PDF format)", type=["pdf"])
    job_description = str.text_area("Paste the Job Description (JD)", height=300, placeholder="Paste the target job role details here...")
    
    submit_button = str.button("Analyze Alignment", type="primary", use_container_width=True)

# Processing Logic
if submit_button:
    if not uploaded_file:
        str.error("Please upload your PDF resume first.")
    elif not job_description.strip():
        str.error("Please paste a Job Description to match against.")
    else:
        with str.spinner("Extracting resume contents and communicating with n8n workflow..."):
            try:
                # 1. Local Free PDF Text Extraction
                reader = PdfReader(uploaded_file)
                resume_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        resume_text += text + "\n"
                
                if not resume_text.strip():
                    raise ValueError("Could not extract legible text from the uploaded PDF.")

                # 2. Construct Payload
                payload = {
                    "resume_text": resume_text,
                    "job_description": job_description
                }

                # 3. HTTP POST to Local n8n Webhook
                response = requests.post(webhook_url, json=payload, timeout=60)
                
                # 4. Handle Response
                if response.status_code == 200:
                    try:
                        str.session_state.analysis_result = response.json()
                        str.success("Analysis Complete!")
                    except json.JSONDecodeError:
                        str.error("Workflow responded, but the output was not valid JSON.")
                        str.text(response.text)
                else:
                    str.error(f"n8n returned an error status code: {response.status_code}")
                    str.text(response.text)

            except requests.exceptions.ConnectionError:
                str.error("Could not connect to n8n. Verify that your local n8n instance is active at the provided URL.")
            except Exception as e:
                str.error(f"An unexpected error occurred: {str(e)}")

# Display Results
with col2:
    str.subheader("AI Evaluation Dashboard")
    
    if str.session_state.analysis_result:
        data = str.session_state.analysis_result
        
        # Metric Cards
        match_pct = data.get("match_percentage", 0)
        str.metric(label="Overall Match Score", value=f"{match_pct}%")
        str.progress(match_pct / 100)
        
        str.write("---")
        
        # Two-Column Skills Analysis
        sk_col1, sk_col2 = str.columns(2)
        with sk_col1:
            str.markdown("### ✅ Identified Skills")
            for skill in data.get("candidate_skills", []):
                str.markdown(f"- {skill}")
                
        with sk_col2:
            str.markdown("### ⚠️ Missing Skills / Gaps")
            for skill in data.get("missing_skills", []):
                str.markdown(f"- <span style='color:#ff4b4b'>{skill}</span>", unsafe_allow_html=True)
                
        str.write("---")
        
        # Interview Prep Expandable Sections
        str.markdown("### 🎯 Interview Preparation Strategy")
        tips = data.get("interview_prep_tips", [])
        if tips:
            for i, tip in enumerate(tips, 1):
                with str.expander(f"Strategy {i}: {tip.split(':')[0] if ':' in tip else 'Preparation Tip'}"):
                    str.write(tip)
        else:
            str.info("No explicit interview preparation tips generated.")
            
    else:
        str.info("Awaiting input data. Fill out the forms on the left and trigger the analysis engine.")