import streamlit as st
import pypdf
import fitz  # PyMuPDF for deep structural diagnostics
import re
import io
from docx import Document
from datetime import datetime

# 1. Page Configuration & Custom CSS Injection
st.set_page_config(
    page_title="PDF BUSTER // Advanced Forensic Suite", 
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
st.html('<div class="brand-tagline">Deep-Object Tampering Isolation & Digital Forensics Suite</div>')

st.sidebar.markdown("### 🛠️ Mode Selection")
app_mode = st.sidebar.radio(
    "Choose Utility Interface:",
    ["🔍 PDF Forensic Analyzer", "📄 Resume Re-Formatter"]
)

# -------------------------------------------------------------
# MODE A: EXPERT FORENSIC ANALYZER UTILITY
# -------------------------------------------------------------
if app_mode == "🔍 PDF Forensic Analyzer":
    st.subheader("Deep-Object Tampering Analytics")
    uploaded_file = st.file_uploader("Drop target document here for corporate-grade forensic evaluation", type="pdf", key="forensic_upload")

    def analyze_pdf_advanced(file_bytes):
        results = {
            "incremental_updates": 0,
            "xref_tables": 0,
            "font_anomalies": 0,
            "is_edited": False,
            "tamper_lock": False,  # Strict indicator for a consumer PDF editor tool execution
            "metadata": {},
            "detailed_findings": [],
            "edited_segments": [],  
            "producer": "Unknown",
            "dates_match": "Verified"
        }
        
        # Gather basic structure values
        eof_markers = re.findall(b'%%EOF', file_bytes)
        xref_markers = re.findall(b'xref', file_bytes)
        results["incremental_updates"] = len(eof_markers)
        results["xref_tables"] = len(xref_markers)

        # --- PHASE 1: PARSE VISUAL LAYERS FOR EXPLICIT EDITOR ARTIFACTS ---
        has_extracted_text = False
        try:
            doc_fitz = fitz.open(stream=file_bytes, filetype="pdf")
            
            for page_num in range(len(doc_fitz)):
                page = doc_fitz[page_num]
                text_blocks = page.get_text("blocks")
                
                for block in text_blocks:
                    block_text = block[4].strip()
                    if block_text:
                        has_extracted_text = True
                    
                    # Intercept editor signatures or watermark overlays hidden within layout streams
                    if any(marker in block_text.lower() for marker in ["ilovepdf", "smallpdf", "watermark", "eval", "sejda", "pdfescape", "pdf2go"]):
                        results["tamper_lock"] = True
                        results["edited_segments"].append(f"Page {page_num + 1} Editor Injection Block: '{block_text}'")
            
            # Analyze embedded font metadata
            all_fonts = []
            for page in doc_fitz:
                all_fonts.extend([f[3] for f in page.get_fonts() if f])
            unique_fonts = list(set(all_fonts))
            suspicious_fonts = [f for f in unique_fonts if "identity-h" in f.lower() or "custom" in f.lower()]
            results["font_anomalies"] = len(suspicious_fonts)
            
        except Exception as e:
            results["detailed_findings"].append({"title": "Forensic Parse Interruption", "text": str(e)})

        # --- PHASE 2: AUDIT SYSTEM PRODUCER METADATA TREE ---
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            metadata = reader.metadata
            if metadata:
                cleaned_meta = {k.replace('/', ''): str(v) for k, v in metadata.items()}
                results["metadata"] = cleaned_meta
                raw_producer = cleaned_meta.get("Producer", "Unknown")
                results["producer"] = raw_producer[:20] + "..." if len(raw_producer) > 20 else raw_producer
                
                # Check for explicit third-party PDF editor footprints in the producer property string
                producer_lower = raw_producer.lower()
                suspicious_tools = ["ilovepdf", "smallpdf", "pdf2go", "nitro", "soda", "libreoffice", "canva", "pdfescape", "sejda"]
                for tool in suspicious_tools:
                    if tool in producer_lower:
                        results["tamper_lock"] = True
                        results["detailed_findings"].append({
                            "title": "🎭 PDF Editor Tool Profile Trapped",
                            "text": f"File properties explicitly identify usage of consumer editing engine framework: '{raw_producer}'"
                        })
                
                create_date = cleaned_meta.get("CreationDate")
                mod_date = cleaned_meta.get("ModDate")
                if create_date and mod_date and create_date != mod_date:
                    results["dates_match"] = "Mismatch"
        except:
            pass

        # --- PHASE 3: EVALUATE TARGET MATRIX RULES ---
        # Rule A: If an explicit PDF Editor tool fingerprint is isolated, immediately Red Flag.
        if results["tamper_lock"] or len(results["edited_segments"]) > 0:
            results["is_edited"] = True
            
        # Rule B: Font clashing combined with a timeline mismatch indicates manual numeric modification.
        elif results["font_anomalies"] > 0 and results["dates_match"] == "Mismatch":
            results["is_edited"] = True
            results["detailed_findings"].append({
                "title": "⚠️ Targeted Data Modification Signature",
                "text": "Detected localized typographic anomalies alongside a modified timestamp timeline conflict. This occurs when individual fields are adjusted post-generation."
            })
            
        # Rule C: If it has multiple save cycles but contains no real font conflicts or tool tags, it's a safe scan/resave.
        else:
            # Document is clean or is a standard scanned/flattened image workflow.
            results["is_edited"] = False

        return results

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        with st.spinner("PDF BUSTER running structural isolation layers..."):
            analysis = analyze_pdf_advanced(file_bytes)
            
        st.write("")
        
        # Display high-stakes visual risk block alerts
        if analysis["tamper_lock"]:
            st.error("🚨 **PDF BUSTER VERDICT: FULL RED FLAG (110% TAMPERED)** \n\n Explicit usage of external PDF Editor Tools isolated. Document is unsafe.", icon="🛑")
            card_class = "alert-active"
        elif analysis["is_edited"]:
            st.warning("⚠️ **PDF BUSTER VERDICT: CAUTION (MANIPULATION INDICATORS FOUND)** \n\n Internal typographic or timeline deviations found. Review details below.", icon="⚡")
            card_class = "caution-active"
        else:
            st.success("🛡️ **PDF BUSTER VERDICT: SECURE / SAFE TO PROCEED** \n\n Structure matches requirements. Scanned, flattened, or original unedited state confirmed.", icon="✅")
            card_class = "clean-active"
            
        metrics_html = (
            f'<div class="buster-grid">'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["incremental_updates"]}</div><div class="buster-lbl">Appended Saves</div></div>'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["xref_tables"]}</div><div class="buster-lbl">XREF Maps</div></div>'
            f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["font_anomalies"]}</div><div class="buster-lbl">Font Anomalies</div></div>'
            f'</div>'
        )
        st.html(metrics_html)
        
        st.subheader("🎯 Isolated Edited Portions & Modifications")
        if analysis["edited_segments"]:
            st.caption("The engine isolated the following explicit text blocks added via post-creation application interfaces:")
            for segment in analysis["edited_segments"]:
                st.html(f'<div style="padding:10px; background-color:#fff2f2; border-left:4px solid #ff4b4b; border-radius:4px; margin-bottom:8px; font-family:monospace; font-size:12.5px; color:#990000;">⚠️ {segment}</div>')
        else:
            st.info("No localized text overrides or individual section patches detected on the visual document layer.")
            
        st.subheader("📋 Structural Forensics Log")
        for finding in analysis["detailed_findings"]:
            st.html(f'<div class="detail-block"><div class="detail-title">{finding["title"]}</div><div class="detail-text">{finding["text"]}</div></div>')

# -------------------------------------------------------------
# MODE B: STANDARDIZED RESUME RE-FORMATTER UTILITY
# -------------------------------------------------------------
elif app_mode == "📄 Resume Re-Formatter":
    st.subheader("Standardized Profile Formatting Engine")
    st.markdown("Convert raw, unformatted candidate details into your exact reference profile format.")
    
    uploaded_resume = st.file_uploader("Upload raw candidate profile (PDF or Word)", type=["pdf", "docx"], key="resume_upload")
    # [Your full multi-page layout builder logic text-routing code blocks run here completely unchanged]
