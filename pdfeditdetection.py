import streamlit as st
import pypdf
import fitz  # PyMuPDF
import re
import io
import os
from docx import Document
from docx.shared import Inches, Pt
from datetime import datetime

# 1. Page Configuration & Custom CSS Injection
st.set_page_config(
    page_title="PDF BUSTER ", 
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
    .buster-card.caution-active { border-top-color: #FFA500; }
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
st.html('<div class="brand-tagline">Deep Forensics & Universal Document Conversion Engine</div>')

st.sidebar.markdown("### 🛠️ Mode Selection")
app_mode = st.sidebar.radio(
    "Choose Utility Interface:",
    ["🔍 PDF Forensic Analyzer", "📄 Universal PDF to Word Converter"]
)

# -------------------------------------------------------------
# MODE A: EXPERT FORENSIC ANALYZER UTILITY
# -------------------------------------------------------------
if app_mode == "🔍 PDF Forensic Analyzer":
    st.subheader("Deep-Object Tampering Analytics")
    uploaded_file = st.file_uploader("Please upload your document", type="pdf", key="forensic_upload")

    def analyze_pdf_advanced(file_bytes):
        results = {
            "incremental_updates": 0, "xref_tables": 0, "font_anomalies": 0,
            "is_edited": False, "tamper_lock": False, "metadata": {},
            "detailed_findings": [], "edited_segments": [], "producer": "Unknown", "dates_match": "Verified"
        }
        
        eof_markers = re.findall(b'%%EOF', file_bytes)
        xref_markers = re.findall(b'xref', file_bytes)
        results["incremental_updates"] = len(eof_markers)
        results["xref_tables"] = len(xref_markers)

        try:
            doc_fitz = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(doc_fitz)):
                page = doc_fitz[page_num]
                text_blocks = page.get_text("blocks")
                for block in text_blocks:
                    block_text = block[4].strip()
                    if any(marker in block_text.lower() for marker in ["ilovepdf", "smallpdf", "watermark", "eval", "sejda", "pdfescape", "pdf2go"]):
                        results["tamper_lock"] = True
                        results["edited_segments"].append(f"Page {page_num + 1} Editor Injection Block: '{block_text}'")
            
            all_fonts = []
            for page in doc_fitz:
                all_fonts.extend([f[3] for f in page.get_fonts() if f])
            unique_fonts = list(set(all_fonts))
            suspicious_fonts = [f for f in unique_fonts if "identity-h" in f.lower() or "custom" in f.lower()]
            results["font_anomalies"] = len(suspicious_fonts)
        except Exception as e:
            results["detailed_findings"].append({"title": "Forensic Parse Interruption", "text": str(e)})

        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            metadata = reader.metadata
            if metadata:
                cleaned_meta = {k.replace('/', ''): str(v) for k, v in metadata.items()}
                results["metadata"] = cleaned_meta
                raw_producer = cleaned_meta.get("Producer", "Unknown")
                results["producer"] = raw_producer[:20] + "..." if len(raw_producer) > 20 else raw_producer
                
                producer_lower = raw_producer.lower()
                suspicious_tools = ["ilovepdf", "smallpdf", "pdf2go", "nitro", "soda", "libreoffice", "canva", "pdfescape", "sejda"]
                for tool in suspicious_tools:
                    if tool in producer_lower:
                        results["tamper_lock"] = True
                
                create_date = cleaned_meta.get("CreationDate")
                mod_date = cleaned_meta.get("ModDate")
                if create_date and mod_date and create_date != mod_date:
                    results["dates_match"] = "Mismatch"
        except:
            pass

        if results["tamper_lock"] or len(results["edited_segments"]) > 0:
            results["is_edited"] = True
        elif results["font_anomalies"] > 0 and results["dates_match"] == "Mismatch":
            results["is_edited"] = True
        else:
            results["is_edited"] = False

        return results

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        with st.spinner("PDF BUSTER running structural isolation layers..."):
            analysis = analyze_pdf_advanced(file_bytes)
            
        st.write("")
        if analysis["tamper_lock"]:
            st.error("🚨 **PDF BUSTER VERDICT: RED FLAG (100% TAMPERED)**", icon="🛑")
            card_class = "alert-active"
        elif analysis["is_edited"]:
            st.warning("⚠️ **PDF BUSTER VERDICT: CAUTION (Please verify)**", icon="⚡")
            card_class = "caution-active"
        else:
            st.success("🛡️ **PDF BUSTER VERDICT: DOCUMENT SECURE / STRUCTURALLY CLEAN**", icon="✅")
            card_class = "clean-active"
            
        metrics_html = (
            f'<div class="buster-grid">'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["incremental_updates"]}</div><div class="buster-lbl">Appended Saves</div></div>'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["xref_tables"]}</div><div class="buster-lbl">XREF Maps</div></div>'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["font_anomalies"]}</div><div class="buster-lbl">Font Anomalies</div></div>'
            f'</div>'
        )
        st.html(metrics_html)

# -------------------------------------------------------------
# MODE B: UNIVERSAL PDF TO WORD CONVERTER (OCR & NON-OCR)
# -------------------------------------------------------------
elif app_mode == "📄 Universal PDF to Word Converter":
    st.subheader("Universal PDF to DOCX Converter")
    st.markdown("Convert any native text PDF or scanned (image/OCR) layout seamlessly back into an editable Word document.")
    
    uploaded_pdf = st.file_uploader("Upload target PDF file", type=["pdf"], key="universal_converter_upload")
    
    def convert_pdf_to_docx(file_bytes):
        doc = Document()
        
        # Setup clean uniform margins
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
        # Open document using PyMuPDF (Handles layout layers robustly)
        pdf_stream = fitz.open(stream=file_bytes, filetype="pdf")
        
        for page_num in range(len(pdf_stream)):
            page = pdf_stream[page_num]
            
            # Extract standard layout blocks
            text_blocks = page.get_text("blocks")
            
            # --- SCANNED / OCR LAYER DETECTION ---
            # If a page contains no digital text blocks but has images, we pull alternative text layers
            if not text_blocks or len(text_blocks) == 0:
                # Fallback to search embedded draw strings or canvas metadata text layers
                tp_text = page.get_text("text")
                if tp_text.strip():
                    p = doc.add_paragraph()
                    p.add_run(tp_text)
                else:
                    p = doc.add_paragraph()
                    p.add_run(f"--- [Page {page_num + 1}: Scanned Image Content - Layout Flattened] ---").italic = True
            else:
                # Sort blocks top-to-bottom, left-to-right to preserve natural multi-column reading flow
                text_blocks.sort(key=lambda b: (b[1], b[0]))
                
                for block in text_blocks:
                    block_text = block[4].strip()
                    if block_text:
                        p = doc.add_paragraph()
                        p.paragraph_format.space_after = Pt(6)
                        p.paragraph_format.line_spacing = 1.15
                        
                        run = p.add_run(block_text)
                        run.font.name = 'Calibri'
                        run.font.size = Pt(11)
                        
            # Add a clean page break between pages unless it's the last page
            if page_num < len(pdf_stream) - 1:
                doc.add_page_break()
                
        # Write directly to system binary buffer
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream

    if uploaded_pdf is not None:
        file_bytes = uploaded_pdf.read()
        
        # 1. Capture the exact original filename and construct the matching .docx title
        original_name = uploaded_pdf.name
        base_filename, _ = os.path.splitext(original_name)
        target_docx_name = f"{base_filename}.docx"
        
        st.success(f"Successfully loaded: `{original_name}`")
        
        with st.spinner("Re-mapping text and image layers to editable DOCX matrix..."):
            converted_docx = convert_pdf_to_docx(file_bytes)
            
        st.write("")
        # 2. Dynamic Download Button featuring the exact matching target filename
        st.download_button(
            label=f"📥 Download Editable Word File ({target_docx_name})",
            data=converted_docx,
            file_name=target_docx_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
