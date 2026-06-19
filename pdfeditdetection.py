import streamlit as st
import pypdf
import re
import io
from docx import Document
from datetime import datetime

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="PDF BUSTER // Recruitment Core", 
    page_icon="💥", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

STYLE_INJECTION = """
<style>
    .brand-title { font-family: 'Courier New', Courier, monospace; font-size: 40px; font-weight: 900; letter-spacing: -1px; color: #FF4B4B; margin-bottom: 0px; display: flex; align-items: center; gap: 10px; }
    .brand-tagline { color: #6c757d; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 30px; border-bottom: 2px solid #efefef; padding-bottom: 10px; }
    .buster-grid { display: flex; justify-content: space-between; gap: 15px; margin-top: 20px; margin-bottom: 25px; }
    .buster-card { background-color: #f8f9fa; border: 1px solid #e9ecef; border-top: 4px solid #6c757d; border-radius: 6px; padding: 18px; flex: 1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .buster-card.alert-active { border-top-color: #FF4B4B; }
    .buster-card.clean-active { border-top-color: #28a745; }
    .buster-val { font-size: 26px; font-weight: 800; font-family: monospace; margin-bottom: 4px; }
    .buster-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #6c757d; font-weight: 600; }
    .detail-block { padding: 15px; border-radius: 6px; background-color: #fafafa; border-left: 4px solid #007bd9; margin-bottom: 12px; }
    .detail-title { font-weight: 700; font-size: 15px; margin-bottom: 4px; color: #1f2937; }
    .detail-text { font-size: 13.5px; color: #4b5563; line-height: 1.5; }
</style>
"""
st.html(STYLE_INJECTION)

st.html('<div class="brand-title">💥 PDF BUSTER</div>')
st.html('<div class="brand-tagline">Automated Digital Tampering & Workforce Automation Suite</div>')

st.sidebar.markdown("### 🛠️ Mode Selection")
app_mode = st.sidebar.radio(
    "Choose Utility Interface:",
    ["🔍 PDF Forensic Analyzer", "📄 Resume Re-Formatter"]
)

# -------------------------------------------------------------
# MODE A: FORENSIC ANALYZER UTILITY
# -------------------------------------------------------------
if app_mode == "🔍 PDF Forensic Analyzer":
    st.subheader("Document Tampering Isolation")
    uploaded_file = st.file_uploader("Drop target document here for structural analysis", type="pdf", key="forensic_upload")

    def analyze_pdf(file_bytes):
        results = {"incremental_updates": 0, "is_edited": False, "metadata": {}, "detailed_findings": [], "producer": "Unknown", "dates_match": "Verified"}
        eof_markers = re.findall(b'%%EOF', file_bytes)
        results["incremental_updates"] = len(eof_markers)
        if len(eof_markers) > 1:
            results["is_edited"] = True
            results["detailed_findings"].append({
                "title": "Incremental Save Signature Isolated",
                "text": f"Detected {len(eof_markers)} distinct End-Of-File (%%EOF) markers. Multiple markers indicate post-creation editing loops."
            })
        else:
            results["detailed_findings"].append({"title": "Binary Structure Integrity", "text": "File contains exactly 1 %%EOF token. Standard standalone compilation pattern matches."})

        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            metadata = reader.metadata
            if metadata:
                cleaned_meta = {k.replace('/', ''): str(v) for k, v in metadata.items()}
                results["metadata"] = cleaned_meta
                raw_producer = cleaned_meta.get("Producer", "Unknown")
                results["producer"] = raw_producer[:20] + "..." if len(raw_producer) > 20 else raw_producer
                create_date = cleaned_meta.get("CreationDate")
                mod_date = cleaned_meta.get("ModDate")
                if create_date and mod_date and create_date != mod_date:
                    results["is_edited"] = True
                    results["dates_match"] = "Mismatch"
                    results["detailed_findings"].append({"title": "Timeline Synchronization Failure", "text": "Creation Date and Modification Date tags are misaligned, pointing to manual save iterations."})
                else:
                    results["dates_match"] = "Aligned"
            else:
                results["is_edited"] = True
                results["dates_match"] = "Wiped"
                results["detailed_findings"].append({"title": "Anomalous Container: Blank Object Dictionary", "text": "Metadata lookup dictionary is empty. High probability file history was intentionally stripped."})
        except Exception as e:
            results["detailed_findings"].append({"title": "Parsing Interruption", "text": str(e)})
        return results

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        with st.spinner("Processing structural isolation layers..."):
            analysis = analyze_pdf(file_bytes)
        st.write("")
        if analysis["is_edited"]:
            st.error("💥 **PDF BUSTER VERDICT: DOCUMENT MODIFICATIONS ISOLATED**", icon="🚨")
            card_class = "alert-active"
        else:
            st.success("🛡️ **PDF BUSTER VERDICT: SECURE / NO MANIPULATION DETECTED**", icon="✅")
            card_class = "clean-active"
            
        metrics_html = (
            f'<div class="buster-grid">'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["incremental_updates"]}</div><div class="buster-lbl">Save Cycles</div></div>'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["dates_match"]}</div><div class="buster-lbl">Timeline Sync</div></div>'
            f'<div class="buster-card {card_class}"><div class="buster-val" style="font-size:13px; padding-top:10px; overflow:hidden;">{analysis["producer"]}</div><div class="buster-lbl">Core Engine</div></div>'
            f'</div>'
        )
        st.html(metrics_html)
        for finding in analysis["detailed_findings"]:
            st.html(f'<div class="detail-block"><div class="detail-title">🔹 {finding["title"]}</div><div class="detail-text">{finding["text"]}</div></div>')

# -------------------------------------------------------------
# MODE B: TEMPLATE RESUME RE-FORMATTER UTILITY
# -------------------------------------------------------------
elif app_mode == "📄 Resume Re-Formatter":
    st.subheader("Template-Driven Resume Re-Formatter")
    st.markdown("Ensure compliance and brand uniformity by matching an exact styling format.")
    
    # 1. Template Upload Section
    st.write("##### 1. Establish Layout Standard")
    template_file = st.file_uploader(
        "Upload your blank Master Sample Resume format (.docx containing keys like [CANDIDATE_NAME] or [RESUME_BODY])", 
        type=["docx"], 
        key="template_upload"
    )
    
    # 2. Raw Candidate File Upload Section
    st.write("##### 2. Upload Targeted Candidate Data")
    uploaded_resume = st.file_uploader("Upload raw candidate profile (PDF or Word)", type=["pdf", "docx"], key="resume_upload")
    
    def inject_into_template(template_bytes, candidate_text):
        doc = Document(io.BytesIO(template_bytes))
        
        lines = [line.strip() for line in candidate_text.split('\n') if line.strip()]
        candidate_name = lines[0] if lines else "Candidate Profile"
        full_body_text = "\n".join(lines[1:]) if len(lines) > 1 else "No text extracted."
        
        for paragraph in doc.paragraphs:
            if "[CANDIDATE_NAME]" in paragraph.text:
                paragraph.text = paragraph.text.replace("[CANDIDATE_NAME]", candidate_name)
            if "[RESUME_BODY]" in paragraph.text:
                paragraph.text = paragraph.text.replace("[RESUME_BODY]", full_body_text)
                
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if "[CANDIDATE_NAME]" in paragraph.text:
                            paragraph.text = paragraph.text.replace("[CANDIDATE_NAME]", candidate_name)
                        if "[RESUME_BODY]" in paragraph.text:
                            paragraph.text = paragraph.text.replace("[RESUME_BODY]", full_body_text)

        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream

    if template_file is not None and uploaded_resume is not None:
        raw_text = ""
        
        if uploaded_resume.name.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(uploaded_resume)
                for page in reader.pages:
                    chunk = page.extract_text()
                    if chunk:
                        raw_text += chunk + "\n"
            except Exception as e:
                st.error(f"Could not parse incoming PDF: {e}")
        elif uploaded_resume.name.endswith('.docx'):
            try:
                doc_in = Document(uploaded_resume)
                for para in doc_in.paragraphs:
                    if para.text:
                        raw_text += para.text + "\n"
            except Exception as e:
                st.error(f"Could not read incoming Docx paragraph structures: {e}")
                
        if raw_text.strip():
            st.success("Target text extracted successfully! Ready to re-map structure.")
            
            with st.spinner("Injecting candidate text alignment into your Sample Master Template..."):
                template_bytes = template_file.read()
                processed_docx = inject_into_template(template_bytes, raw_text)
                
            st.write("")
            st.download_button(
                label="📥 Download Standardized Word File (.docx)",
                data=processed_docx,
                file_name=f"Formatted_Profile_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    elif template_file is None and uploaded_resume is not None:
        st.info("💡 Please upload your blank master sample document template first above to match your branding format parameters.")
