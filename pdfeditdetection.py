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
# MODE B: STANDARDIZED RESUME RE-FORMATTER UTILITY
# -------------------------------------------------------------
elif app_mode == "📄 Resume Re-Formatter":
    st.subheader("Standardized Profile Formatting Engine")
    st.markdown("Convert raw, unformatted candidate details into your exact reference profile format.")
    
    uploaded_resume = st.file_uploader("Upload raw candidate profile (PDF or Word)", type=["pdf", "docx"], key="resume_upload")
    
    def build_sample_aligned_format(candidate_text):
        doc = Document()
        
        # 1. Page Setup (Clean 1" Professional Margins)
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
        # 2. Reference Style Scheme (Clean Corporate Black/Charcoal)
        COLOR_PRIMARY = RGBColor(0, 0, 0)         # Stark bold black headings
        COLOR_BODY = RGBColor(40, 44, 52)         # Deep charcoal reader text
        FONT_NAME = 'Calibri'                     # Matching sample font framework
        
        # Extract name and clean structural string segments
        lines = [line.strip() for line in candidate_text.split('\n') if line.strip()]
        candidate_name = lines[0] if lines else "CANDIDATE PROFILE"
        
        # Structural Section Generator Helper
        def add_sample_heading(title_text):
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(14)
            p_space.paragraph_format.space_after = Pt(2)
            
            p_heading = doc.add_paragraph()
            p_heading.paragraph_format.space_after = Pt(4)
            p_heading.paragraph_format.keep_with_next = True
            run_h = p_heading.add_run(title_text)
            run_h.font.name = FONT_NAME
            run_h.font.size = Pt(13)
            run_h.bold = True
            run_h.font.color.rgb = COLOR_PRIMARY
            
        # --- SAMPLE FORMAT HEADER LAYER ---
        p_name = doc.add_paragraph()
        p_name.paragraph_format.space_after = Pt(2)
        run_name = p_name.add_run(candidate_name)
        run_name.font.name = FONT_NAME
        run_name.font.size = Pt(18)
        run_name.bold = True
        run_name.font.color.rgb = COLOR_PRIMARY
        
        # Metadata Sub-Header Layout (Email | LinkedIn Links)
        p_links = doc.add_paragraph()
        p_links.paragraph_format.space_after = Pt(12)
        run_links = p_links.add_run("Email: contact@candidate.com  |  LinkedIn: linkedin.com/in/candidate")
        run_links.font.name = FONT_NAME
        run_links.font.size = Pt(10)
        run_links.font.color.rgb = RGBColor(100, 110, 120)
        
        # --- SECTION 1: PROFESSIONAL SUMMARY ---
        add_sample_heading("Professional Summary")
        p_summary = doc.add_paragraph()
        p_summary.paragraph_format.space_after = Pt(6)
        p_summary.paragraph_format.line_spacing = 1.15
        summary_base = "Results-driven professional with specialized capabilities across core execution platforms. Experienced in stakeholder alignment, cross-functional project management, and scalable workflows within high-stakes market sectors."
        run_sum = p_summary.add_run(summary_base)
        run_sum.font.name = FONT_NAME
        run_sum.font.size = Pt(11)
        run_sum.font.color.rgb = COLOR_BODY

        # --- SECTION 2: SKILLS MATRIX ---
        add_sample_heading("Skills")
        p_skills = doc.add_paragraph()
        p_skills.paragraph_format.space_after = Pt(6)
        p_skills.paragraph_format.line_spacing = 1.15
        skills_base = "Core Deliverables • Pipeline Management • Optimization Systems • Analytics Tracking • Cross-Functional Team Leadership"
        run_skills = p_skills.add_run(skills_base)
        run_skills.font.name = FONT_NAME
        run_skills.font.size = Pt(11)
        run_skills.font.color.rgb = COLOR_BODY

        # --- SECTION 3: CHRONOLOGICAL EXPERIENCE ---
        add_sample_heading("Professional Experience")
        
        # Loop first 50 content fragments cleanly into your bullet array format
        body_source_lines = lines[1:50] if len(lines) > 1 else ["No additional performance parameters extracted."]
        for line in body_source_lines:
            p_bullet = doc.add_paragraph(style='List Bullet')
            p_bullet.paragraph_format.space_after = Pt(3)
            p_bullet.paragraph_format.line_spacing = 1.15
            
            run_b = p_bullet.add_run(line)
            run_b.font.name = FONT_NAME
            run_b.font.size = Pt(11)
            run_b.font.color.rgb = COLOR_BODY
            
        # Secure memory buffer stream
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream

    if uploaded_resume is not None:
        raw_text = ""
        
        # Extraction layer pipelines
        if uploaded_resume.name.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(uploaded_resume)
                for page in reader.pages:
                    chunk = page.extract_text()
                    if chunk:
                        raw_text += chunk + "\n"
            except Exception as e:
                st.error(f"Could not parse incoming PDF framework: {e}")
        elif uploaded_resume.name.endswith('.docx'):
            try:
                doc_in = Document(uploaded_resume)
                for para in doc_in.paragraphs:
                    if para.text:
                        raw_text += para.text + "\n"
            except Exception as e:
                st.error(f"Could not read incoming Docx paragraph schema: {e}")
                
        if raw_text.strip():
            st.success("Target text extracted successfully! Ready to standardize.")
            
            with st.spinner("Assembling custom formatting matrix into locked sample style..."):
                processed_docx = build_sample_aligned_format(raw_text)
                
            st.write("")
            st.download_button(
                label="📥 Download Standardized Word File (.docx)",
                data=processed_docx,
                file_name=f"Buster_Formatted_Profile_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        else:
            st.warning("Could not gather clear text segments from this profile layout.")
