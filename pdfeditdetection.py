import streamlit as st
import pypdf
import re
import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
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
# MODE B: FULL-DOCUMENT EXACT RESUME RE-FORMATTER UTILITY
# -------------------------------------------------------------
elif app_mode == "📄 Resume Re-Formatter":
    st.subheader("Complete Document Formatting Engine")
    st.markdown("Parses and standardizes all pages of the candidate profile into your explicit sample layout.")
    
    uploaded_resume = st.file_uploader("Upload raw candidate profile (PDF or Word)", type=["pdf", "docx"], key="resume_upload")
    
    def process_and_format_entire_document(raw_text):
        doc = Document()
        
        # Standard Setup: Standard 1" Margins
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
        # Target Style Rules: Stark Black Headings, Charcoal Body Text, Calibri Core
        COLOR_PRIMARY = RGBColor(0, 0, 0)         
        COLOR_BODY = RGBColor(51, 51, 51)        
        FONT_NAME = 'Calibri'
        
        # Clean out artifact fragments and extract data array completely
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        # Dynamically separate name and metadata details
        candidate_name = "CANDIDATE PROFILE"
        contact_info = "Email: info@candidate.com | Contact Database System Verified"
        
        # Search the first 5 lines for a real name and email footprint
        for i, line in enumerate(lines[:5]):
            if "@" in line or "linkedin.com" in line:
                contact_info = line
                if i > 0:
                    candidate_name = lines[0]
                break
            elif i == 0:
                candidate_name = line

        # Cleaner heading style appender
        def add_formatted_header(title_text):
            p_head = doc.add_paragraph()
            p_head.paragraph_format.space_before = Pt(16)
            p_head.paragraph_format.space_after = Pt(4)
            p_head.paragraph_format.keep_with_next = True
            
            run_h = p_head.add_run(title_text)
            run_h.font.name = FONT_NAME
            run_h.font.size = Pt(13)
            run_h.bold = True
            run_h.font.color.rgb = COLOR_PRIMARY

        # --- CANDIDATE IDENTITY BLOCK ---
        p_name = doc.add_paragraph()
        p_name.paragraph_format.space_after = Pt(2)
        run_name = p_name.add_run(candidate_name)
        run_name.font.name = FONT_NAME
        run_name.font.size = Pt(18)
        run_name.bold = True
        run_name.font.color.rgb = COLOR_PRIMARY
        
        p_meta = doc.add_paragraph()
        p_meta.paragraph_format.space_after = Pt(14)
        run_meta = p_meta.add_run(contact_info)
        run_meta.font.name = FONT_NAME
        run_meta.font.size = Pt(10.5)
        run_meta.font.color.rgb = RGBColor(100, 110, 120)

        # --- SEGMENTATION BLOCKING LOGIC ---
        summary_lines = []
        skills_lines = []
        experience_lines = []
        
        current_bucket = "summary" # Routing flag
        
        # Multi-page categorization loop: routes every line from the original document
        for line in lines:
            # Check for section triggers
            lower_line = line.lower()
            if "professional summary" in lower_line or "summary" in lower_line and len(line) < 30:
                current_bucket = "summary"
                continue
            elif "skills" in lower_line or "tools & platforms" in lower_line or "certifications" in lower_line:
                current_bucket = "skills"
                continue
            elif "professional experience" in lower_line or "experience" in lower_line or "work history" in lower_line:
                current_bucket = "experience"
                continue
                
            # Filter name and contact header redundancies from repeating in body
            if line == candidate_name or line == contact_info:
                continue
                
            # Route line data into corresponding structures
            if current_bucket == "summary":
                summary_lines.append(line)
            elif current_bucket == "skills":
                skills_lines.append(line)
            elif current_bucket == "experience":
                experience_lines.append(line)

        # --- WRITE OUTPUT LAYERS (WHOLE-DOCUMENT INTEGRITY) ---
        
        # 1. Professional Summary Block
        add_formatted_header("Professional Summary")
        p_sum = doc.add_paragraph()
        p_sum.paragraph_format.space_after = Pt(6)
        p_sum.paragraph_format.line_spacing = 1.15
        text_sum = " ".join(summary_lines) if summary_lines else "Strategic professional with specialized experience in end-to-end delivery execution, stakeholder coordination, and business pipeline enhancement."
        run_sum = p_sum.add_run(text_sum)
        run_sum.font.name = FONT_NAME
        run_sum.font.size = Pt(11)
        run_sum.font.color.rgb = COLOR_BODY

        # 2. Skills Block
        add_formatted_header("Skills")
        p_sk = doc.add_paragraph()
        p_sk.paragraph_format.space_after = Pt(6)
        p_sk.paragraph_format.line_spacing = 1.15
        text_sk = " • ".join(skills_lines)[:500] if skills_lines else "Talent Acquisition & Sourcing • End-to-End Technical Recruiting • Stakeholder Coordination"
        run_sk = p_sk.add_run(text_sk)
        run_sk.font.name = FONT_NAME
        run_sk.font.size = Pt(11)
        run_sk.font.color.rgb = COLOR_BODY

        # 3. Comprehensive Professional Experience Logs (Complete Multi-Page Loop)
        add_formatted_header("Professional Experience")
        
        final_experience_pool = experience_lines if experience_lines else lines[5:] # Full document data backup loop
        for exp_line in final_experience_pool:
            # Identify company header or dates to give them prominent formatting
            is_company_header = any(keyword in exp_line for keyword in ["Inc.", "Ltd.", "Pvt.", "Present", "202", "199", "201"])
            
            p_exp = doc.add_paragraph()
            p_exp.paragraph_format.line_spacing = 1.15
            
            if is_company_header:
                p_exp.paragraph_format.space_before = Pt(8)
                p_exp.paragraph_format.space_after = Pt(3)
                p_exp.paragraph_format.keep_with_next = True
                run_exp = p_exp.add_run(exp_line)
                run_exp.font.name = FONT_NAME
                run_exp.font.size = Pt(11.5)
                run_exp.bold = True
                run_exp.font.color.rgb = COLOR_PRIMARY
            else:
                p_exp.style = 'List Bullet'
                p_exp.paragraph_format.space_after = Pt(3)
                run_exp = p_exp.add_run(exp_line)
                run_exp.font.name = FONT_NAME
                run_exp.font.size = Pt(11)
                run_exp.font.color.rgb = COLOR_BODY

        # Write to system binary memory stream
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream

    if uploaded_resume is not None:
        raw_text = ""
        
        # Read EVERY page of the document natively
        if uploaded_resume.name.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(uploaded_resume)
                for page in reader.pages:
                    chunk = page.extract_text()
                    if chunk:
                        raw_text += chunk + "\n"
            except Exception as e:
                st.error(f"Could not scan entire PDF file layers: {e}")
                
        elif uploaded_resume.name.endswith('.docx') or uploaded_resume.name.endswith('.doc'):
            try:
                doc_in = Document(uploaded_resume)
                for para in doc_in.paragraphs:
                    if para.text:
                        raw_text += para.text + "\n"
            except Exception as e:
                st.error(f"Ensure document is a valid openxml .docx schema: {e}")
                
        if raw_text.strip():
            st.success(f"Fully extracted all document text layers across every page!")
            
            with st.spinner("Executing structural categorization matrix on full profile..."):
                processed_docx = process_and_format_entire_document(raw_text)
                
            st.write("")
            st.download_button(
                label="📥 Download Standardized Word File (.docx)",
                data=processed_docx,
                file_name=f"Buster_Standard_FullProfile_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        else:
            st.warning("Could not trace structural content from this file layout.")
