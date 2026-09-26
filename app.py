import streamlit as st
import pandas as pd
import tempfile
import os

from modules.docling_parser import extract_pdf_data
from modules.vision import analyze_image
from modules.rag_engine import retrieve_findings
from modules.scoring import calculate_audit_score
from modules.reporting import create_excel_report

st.set_page_config(page_title="Telecom Audit AI", layout="wide")

st.title("📡 Telecom Site Audit AI Engine")
st.markdown("Automated processing of PDF Audit Reports and Field Images for Compliance, Defect Discovery, and Scoring.")

# Sidebar Settings
st.sidebar.header("Configuration")
distance_threshold = st.sidebar.slider("RAG Match Sensitivity", 0.1, 1.0, 0.45, step=0.05)

col1, col2 = st.columns(2)
with col1:
    uploaded_pdfs = st.file_uploader("Upload Telecom PDF Audit Reports", type=["pdf"], accept_multiple_files=True)
with col2:
    uploaded_images = st.file_uploader("Upload Site Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("🚀 Run Audit Engine", type="primary"):
    if not uploaded_pdfs and not uploaded_images:
        st.warning("Please upload at least one PDF report or Site image.")
        st.stop()
        
    results = []
    
    with st.spinner("Analyzing documents and images..."):
        # Process PDFs
        if uploaded_pdfs:
            for pdf in uploaded_pdfs:
                site_id, raw_text = extract_pdf_data(pdf)
                matched_findings = retrieve_findings(raw_text, distance_threshold)
                
                if not matched_findings:
                    matched_findings = ["No issue observed"]
                else:
                    matched_findings = list(set(matched_findings))
                    
                score_meta = calculate_audit_score(matched_findings)
                
                results.append({
                    "Source File": pdf.name,
                    "Site ID": site_id,
                    "Priority": score_meta["priority"],
                    "Health Score": score_meta["health_score"],
                    "Penalty Points": score_meta["penalty_points"],
                    "Findings": " | ".join(matched_findings)
                })

        # Process Standalone Images
        if uploaded_images:
            for img in uploaded_images:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(img.read())
                    tmp_path = tmp.name
                
                try:
                    obs = analyze_image(tmp_path)
                    matched_findings = retrieve_findings(obs, distance_threshold)
                    
                    if not matched_findings:
                        matched_findings = ["No issue observed"]
                    else:
                        matched_findings = list(set(matched_findings))
                        
                    score_meta = calculate_audit_score(matched_findings)
                    
                    results.append({
                        "Source File": img.name,
                        "Site ID": "IMAGE_ONLY",
                        "Priority": score_meta["priority"],
                        "Health Score": score_meta["health_score"],
                        "Penalty Points": score_meta["penalty_points"],
                        "Findings": " | ".join(matched_findings)
                    })
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

    # Display Dashboard Results
    st.subheader("Audit Results Summary")
    res_df = pd.DataFrame(results)
    st.dataframe(res_df, use_container_width=True)
    
    # Export Report
    excel_data = create_excel_report(results)
    st.download_button(
        label="📥 Download Structured Excel Report",
        data=excel_data,
        file_name="Telecom_Audit_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
