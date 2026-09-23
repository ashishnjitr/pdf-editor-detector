import streamlit as st
import pypdf
import fitz  # PyMuPDF
import re
import io
import os
import hashlib
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from docx import Document
from docx.shared import Inches, Pt
from datetime import datetime

# 1. Page Configuration & Custom CSS Injection
st.set_page_config(
    page_title="PDF BUSTER // Legal, Forensic & Suite Core", 
    page_icon="💥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

STYLE_INJECTION = """
<style>
    .brand-title { font-family: 'Courier New', Courier, monospace; font-size: 38px; font-weight: 900; letter-spacing: -1px; color: #FF4B4B; margin-bottom: 0px; display: flex; align-items: center; gap: 10px; }
    .brand-tagline { color: #6c757d; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 25px; border-bottom: 2px solid #efefef; padding-bottom: 10px; }
    .buster-grid { display: flex; justify-content: space-between; gap: 12px; margin-top: 15px; margin-bottom: 20px; }
    .buster-card { background-color: #f8f9fa; border: 1px solid #e9ecef; border-top: 4px solid #6c757d; border-radius: 6px; padding: 14px; flex: 1; text-align: center; }
    .buster-card.alert-active { border-top-color: #FF4B4B; }
    .buster-card.caution-active { border-top-color: #FFA500; }
    .buster-card.clean-active { border-top-color: #28a745; }
    .buster-val { font-size: 22px; font-weight: 800; font-family: monospace; margin-bottom: 2px; }
    .buster-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #6c757d; font-weight: 600; }
    .detail-block { padding: 12px; border-radius: 6px; background-color: #fafafa; border-left: 4px solid #007bd9; margin-bottom: 10px; }
    .detail-title { font-weight: 700; font-size: 14px; margin-bottom: 3px; color: #1f2937; }
    .detail-text { font-size: 13px; color: #4b5563; line-height: 1.4; }
    .evidence-box { padding: 12px; background-color: #fff8f8; border: 1px solid #ffebeb; border-radius: 6px; margin-bottom: 15px; }
    .evidence-item { font-size: 12.5px; font-family: monospace; color: #333; margin-bottom: 4px; }
    .evidence-label { font-weight: bold; color: #c00; }
    .h1b-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-right: 6px; }
    .h1b-pass { background-color: #e6f4ea; color: #137333; }
    .h1b-fail { background-color: #fce8e6; color: #c5221f; }
</style>
"""
st.html(STYLE_INJECTION)

st.html('<div class="brand-title">💥 PDF BUSTER</div>')
st.html('<div class="brand-tagline">Deep Forensics, Pixel-Anomaly Redlining & Document Suite</div>')

st.sidebar.markdown("### 🛠️ Mode Selection")
app_mode = st.sidebar.radio(
    "Choose Utility Interface:",
    [
        "🛂 H-1B (I-797) Tamper & Fraud Detector",
        "🔍 Batch PDF Forensic Analyzer", 
        "📄 Universal PDF to Word Converter",
        "🧼 PDF Privacy Sanitizer & Metadata Wiper"
    ]
)

# -------------------------------------------------------------
# MODE 1: H-1B (I-797) PIXEL & VECTOR FRAUD DETECTOR
# -------------------------------------------------------------
if app_mode == "🛂 H-1B (I-797) Tamper & Fraud Detector":
    st.subheader("H-1B (Form I-797) Fraud, Tamper & Structural Detector")
    st.caption("Screens digital vector layers, text spans, and image-pixel compression matrices to isolate modifications.")
    
    h1b_file = st.file_uploader("Upload H-1B Approval Notice (PDF)", type=["pdf"], key="h1b_uploader")

    sensitivity = st.slider("Detection Sensitivity (Adjust for faint scans)", min_value=15, max_value=60, value=30, step=5)

    def run_image_ela(pil_image, quality=90):
        buffer = io.BytesIO()
        pil_image.save(buffer, 'JPEG', quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer)
        ela_img = ImageChops.difference(pil_image.convert('RGB'), resaved.convert('RGB'))
        extrema = ela_img.getextrema()
        max_diff = max([ex[1] for ex in extrema]) if extrema else 1
        scale = 255.0 / max(max_diff, 1)
        ela_img = ImageEnhance.Brightness(ela_img).enhance(scale)
        return ela_img

    def audit_h1b_copy(file_bytes, ela_thresh):
        audit = {
            "is_tampered": False,
            "receipt_number": "Not Isolated",
            "receipt_valid": False,
            "validity_dates": "Not Isolated",
            "inferred_tool": "None Detected",
            "device_details": "Standard System",
            "tamper_evidence": [],
            "redlined_images": [],
            "flagged_regions_count": 0,
            "risk_score": 0
        }

        # 1. Structural Binary Markers
        eof_markers = re.findall(b'%%EOF', file_bytes)
        xref_markers = re.findall(b'xref', file_bytes)
        has_multi_save = len(eof_markers) > 1 or len(xref_markers) > 1
        
        if has_multi_save:
            audit["risk_score"] += 35
            audit["tamper_evidence"].append(f"Multiple Save Footprint: {len(eof_markers)} %%EOF markers detected.")

        # 2. Metadata Profile
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            metadata = reader.metadata or {}
            cleaned_meta = {k.replace('/', ''): str(v) for k, v in metadata.items()}
            creator = cleaned_meta.get("Creator", "")
            producer = cleaned_meta.get("Producer", "")
            audit["device_details"] = f"{creator} | {producer}".strip(" |") or "Unspecified"
            
            combined_meta = (producer + " " + creator).lower()
            tools = ["ilovepdf", "smallpdf", "pdf2go", "nitro", "soda", "libreoffice", "canva", "pdfescape", "sejda", "photoshop", "gimp", "foxit"]
            for tool in tools:
                if tool in combined_meta:
                    audit["is_tampered"] = True
                    audit["inferred_tool"] = tool.upper()
                    audit["risk_score"] += 50
                    audit["tamper_evidence"].append(f"Editing software signature identified: {tool.upper()}")
        except Exception:
            pass

        # 3. Hybrid Inspection (Text layer + Pixel Artifact Map)
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                flagged_boxes = []

                # USCIS Receipt Check
                receipt_matches = re.findall(r'\b(EAC|WAC|LIN|SRC|IOE|MSC)[\s\-]?(\d{2})[\s\-]?(\d{3})[\s\-]?(\d{5})\b', text, re.IGNORECASE)
                if receipt_matches:
                    prefix, yr, day, code = receipt_matches[0]
                    audit["receipt_number"] = f"{prefix.upper()}{yr}{day}{code}"
                    audit["receipt_valid"] = True
                else:
                    loose_receipt = re.findall(r'\b(EAC|WAC|LIN|SRC|IOE|MSC)[0-9A-Z]{7,12}\b', text, re.IGNORECASE)
                    if loose_receipt:
                        audit["receipt_number"] = loose_receipt[0]
                        audit["receipt_valid"] = False
                        audit["risk_score"] += 40
                        audit["tamper_evidence"].append(f"Irregular Receipt Pattern: '{loose_receipt[0]}'")

                # Validity Window
                date_matches = re.findall(r'(\d{2}/\d{2}/\d{4})\s*(?:to|-|until)\s*(\d{2}/\d{2}/\d{4})', text)
                if date_matches:
                    audit["validity_dates"] = f"{date_matches[0][0]} to {date_matches[0][1]}"

                # Render page to PIL image
                pix = page.get_pixmap(dpi=150)
                pil_img = Image.open(io.BytesIO(pix.tobytes("png")))
                width, height = pil_img.size

                # Pixel ELA Matrix
                ela_image = run_image_ela(pil_img)
                ela_gray = np.array(ela_image.convert('L'))

                # Look for high-frequency patches indicative of spliced text or altered numbers
                grid_step = 25
                for y in range(0, height - grid_step, grid_step):
                    for x in range(0, width - grid_step, grid_step):
                        cell = ela_gray[y:y+grid_step, x:x+grid_step]
                        if np.mean(cell) > (100 - ela_thresh) and np.std(cell) > 15:
                            # Map back to PDF point coordinates
                            scale_x = page.rect.width / width
                            scale_y = page.rect.height / height
                            pdf_rect = fitz.Rect(x * scale_x, y * scale_y, (x + grid_step) * scale_x, (y + grid_step) * scale_y)
                            flagged_boxes.append(pdf_rect)

                # Text Layer Search (Overlays & Secondary Blocks)
                blocks = page.get_text("blocks")
                for block in blocks:
                    block_text = block[4].strip()
                    r = fitz.Rect(block[:4])
                    if any(t in block_text.lower() for t in ["ilovepdf", "smallpdf", "pdfescape", "sejda", "eval"]):
                        flagged_boxes.append(r)
                        audit["risk_score"] += 60

                    # Standalone date/name blocks in files with multiple saves
                    if has_multi_save and len(block_text.split()) <= 3:
                        if re.search(r'(\d{2}/\d{2}/\d{4}|valid|receipt)', block_text, re.IGNORECASE):
                            flagged_boxes.append(r)

                # Cluster and draw flagged boxes
                merged_rects = []
                for rect in flagged_boxes:
                    merged = False
                    for i, m_rect in enumerate(merged_rects):
                        if rect.intersects(m_rect) or abs(rect.y0 - m_rect.y0) < 10:
                            merged_rects[i] = m_rect | rect
                            merged = True
                            break
                    if not merged:
                        merged_rects.append(rect)

                # Draw high-contrast red boxes
                has_page_flags = len(merged_rects) > 0
                for box in merged_rects:
                    audit["flagged_regions_count"] += 1
                    page.draw_rect(box, color=(1, 0, 0), fill=(1, 0, 0), fill_opacity=0.35, width=3.0)
                    page.insert_text((box.x0, max(box.y0 - 4, 10)), "MODIFIED", fontsize=8, color=(1, 0, 0))

                annotated_pix = page.get_pixmap(dpi=150)
                audit["redlined_images"].append((page_num + 1, annotated_pix.tobytes("png"), has_page_flags))

        except Exception as e:
            audit["tamper_evidence"].append(f"Scan interrupted: {str(e)}")

        if audit["flagged_regions_count"] > 0 or audit["inferred_tool"] != "None Detected" or audit["risk_score"] >= 40:
            audit["is_tampered"] = True

        return audit

    if h1b_file is not None:
        file_bytes = h1b_file.read()
        
        with st.spinner("Analyzing document layout and pixel structures..."):
            result = audit_h1b_copy(file_bytes, sensitivity)
            
        st.write("")
        
        if result["is_tampered"]:
            st.error(
                f"🚨 **H-1B VERDICT: MODIFICATIONS DETECTED** \n\n"
                f"Isolated {result['flagged_regions_count']} anomaly cluster(s). Threat Confidence: {min(result['risk_score'] + result['flagged_regions_count'] * 5, 100)}/100.",
                icon="🛑"
            )
        else:
            st.success("🛡️ **H-1B VERDICT: NO MODIFICATIONS DETECTED**", icon="✅")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**USCIS Receipt Number**")
            badge = "h1b-pass" if result["receipt_valid"] else "h1b-fail"
            st.html(f"<span class='h1b-tag {badge}'>{'VALID PATTERN' if result['receipt_valid'] else 'INVALID / MISSING'}</span>")
            st.code(result["receipt_number"])
        with col2:
            st.markdown("**Validity Window**")
            st.info(result["validity_dates"] if result["validity_dates"] != "Not Isolated" else "Dates Not Extracted")
        with col3:
            st.markdown("**Tool Profile**")
            if result["inferred_tool"] != "None Detected":
                st.error(result["inferred_tool"])
            else:
                st.success("None")

        st.markdown("---")
        st.subheader("🎯 Visual Overlay & Coordinates Inspection")
        
        cols = st.columns(min(len(result["redlined_images"]), 2))
        for idx, (p_num, img_b, is_flagged) in enumerate(result["redlined_images"]):
            with cols[idx % 2]:
                caption = f"Page {p_num} {'(🚨 Inconsistencies Highlighted)' if is_flagged else '(Clean Document Grid)'}"
                st.image(img_b, caption=caption, use_container_width=True)

        if result["tamper_evidence"]:
            st.markdown("---")
            st.subheader("📋 Structural Findings")
            for item in result["tamper_evidence"]:
                st.html(f"<div class='detail-block'><div class='detail-title'>⚠️ Structural Signal</div><div class='detail-text'>{item}</div></div>")

# -------------------------------------------------------------
# MODE 2: BATCH FORENSIC ANALYZER
# -------------------------------------------------------------
elif app_mode == "🔍 Batch PDF Forensic Analyzer":
    st.subheader("Batch Forensic Analyzer")
    uploaded_files = st.file_uploader("Upload PDF documents", type="pdf", accept_multiple_files=True, key="batch_upload")
    
    if uploaded_files:
        summary_data = []
        for up_file in uploaded_files:
            b = up_file.read()
            eofs = len(re.findall(b'%%EOF', b))
            xrefs = len(re.findall(b'xref', b))
            verdict = "🛑 Red Flag" if eofs > 1 or xrefs > 1 else "✅ Clean"
            summary_data.append({"Filename": up_file.name, "Verdict": verdict, "Save Cycles": eofs})
        st.dataframe(summary_data, use_container_width=True)

# -------------------------------------------------------------
# MODE 3: UNIVERSAL CONVERTER
# -------------------------------------------------------------
elif app_mode == "📄 Universal PDF to Word Converter":
    st.subheader("PDF to DOCX Converter")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"], key="docx_upload")
    if uploaded_pdf:
        doc = Document()
        pdf_stream = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        for page in pdf_stream:
            text = page.get_text("text")
            if text.strip():
                p = doc.add_paragraph()
                p.add_run(text)
            doc.add_page_break()
        out = io.BytesIO()
        doc.save(out)
        out.seek(0)
        base, _ = os.path.splitext(uploaded_pdf.name)
        st.download_button(f"📥 Download {base}.docx", data=out, file_name=f"{base}.docx", use_container_width=True)

# -------------------------------------------------------------
# MODE 4: PRIVACY SANITIZER
# -------------------------------------------------------------
elif app_mode == "🧼 PDF Privacy Sanitizer & Metadata Wiper":
    st.subheader("Document Sanitizer")
    sanitize_upload = st.file_uploader("Upload PDF", type=["pdf"], key="sanitizer")
    if sanitize_upload:
        src = fitz.open(stream=sanitize_upload.read(), filetype="pdf")
        clean = fitz.open()
        for page in src:
            pix = page.get_pixmap(dpi=200)
            img = fitz.open(stream=pix.tobytes("png"), filetype="png")
            rect = img[0].rect
            pdfbytes = img.convert_to_pdf()
            page_clean = clean.new_page(width=rect.width, height=rect.height)
            page_clean.show_pdf_page(rect, fitz.open("pdf", pdfbytes), 0)
        clean.set_metadata({})
        out = io.BytesIO()
        clean.save(out, garbage=4, deflate=True)
        out.seek(0)
        base, _ = os.path.splitext(sanitize_upload.name)
        st.download_button(f"📥 Download Sanitized PDF", data=out, file_name=f"{base}_sanitized.pdf", use_container_width=True)
