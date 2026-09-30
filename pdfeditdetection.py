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
    page_title="PDF BUSTER // Legal, Forensic & Verification Core", 
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
st.html('<div class="brand-tagline">Deep Forensics, Cross-Document I-797 Fraud Isolation & Verification Engine</div>')

st.sidebar.markdown("### 🛠️ Mode Selection")
app_mode = st.sidebar.radio(
    "Choose Utility Interface:",
    [
        "👥 Dual I-797 Cross-Verification Audit",
        "🛂 Single H-1B (I-797) Fraud Detector",
        "🔍 Batch PDF Forensic Analyzer", 
        "📄 Universal PDF to Word Converter",
        "🧼 PDF Privacy Sanitizer & Metadata Wiper"
    ]
)

# -------------------------------------------------------------
# HELPER: DEEP I-797 ENTITY & TEXT PARSER
# -------------------------------------------------------------
def parse_i797_entities(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
        
    lines = [l.strip() for l in full_text.split('\n') if l.strip()]
    
    # Extract Receipt Number
    receipt = "Not Isolated"
    receipt_valid = False
    r_match = re.search(r'\b(EAC|WAC|LIN|SRC|IOE|MSC)[\s\-]?(\d{2})[\s\-]?(\d{3})[\s\-]?(\d{5})\b', full_text, re.IGNORECASE)
    if r_match:
        prefix, yr, day, code = r_match.groups()
        receipt = f"{prefix.upper()}{yr}{day}{code}"
        receipt_valid = True
    else:
        loose_match = re.search(r'\b(EAC|WAC|LIN|SRC|IOE|MSC)[0-9A-Z]{7,12}\b', full_text, re.IGNORECASE)
        if loose_match:
            receipt = loose_match.group(0).upper()

    # Extract Validity Window
    dates = "Not Isolated"
    d_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*(?:to|-|until)\s*(\d{2}/\d{2}/\d{4})', full_text)
    if d_match:
        dates = f"{d_match.group(1)} to {d_match.group(2)}"

    # Extract Petitioner (Employer) Name
    petitioner = "Not Isolated"
    pet_match = re.search(r'Petitioner\s*[:\n\r]+\s*([A-Za-z0-9\s,\.\-&]{3,50})', full_text, re.IGNORECASE)
    if pet_match:
        petitioner = pet_match.group(1).split('\n')[0].strip()
    else:
        for idx, line in enumerate(lines):
            if "petitioner" in line.lower() and idx + 1 < len(lines):
                candidate = lines[idx + 1]
                if len(candidate) > 2 and not any(k in candidate.lower() for k in ["beneficiary", "receipt", "notice", "case", "page"]):
                    petitioner = candidate
                    break

    # Extract Beneficiary Name
    beneficiary = "Not Isolated"
    ben_match = re.search(r'Beneficiary\s*[:\n\r]+\s*([A-Za-z\s,\.\-]{3,45})', full_text, re.IGNORECASE)
    if ben_match:
        beneficiary = ben_match.group(1).split('\n')[0].strip()
    else:
        for idx, line in enumerate(lines):
            if "beneficiary" in line.lower() and idx + 1 < len(lines):
                candidate = lines[idx + 1]
                if len(candidate) > 2 and not any(k in candidate.lower() for k in ["petitioner", "receipt", "notice", "case", "page"]):
                    beneficiary = candidate
                    break

    return {
        "receipt": receipt,
        "receipt_valid": receipt_valid,
        "dates": dates,
        "petitioner": petitioner,
        "beneficiary": beneficiary,
        "full_text": full_text
    }

# -------------------------------------------------------------
# MODE 1: DUAL I-797 CROSS-VERIFICATION AUDIT
# -------------------------------------------------------------
if app_mode == "👥 Dual I-797 Cross-Verification Audit":
    st.subheader("Dual-Copy Cross-Verification & Conflict Matrix")
    st.caption("Upload two I-797 approval notices for the same candidate to detect template cloning, employer overrides, and shared receipt fraud.")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        copy_1 = st.file_uploader("Upload I-797 Copy #1", type=["pdf"], key="dual_1")
    with col_u2:
        copy_2 = st.file_uploader("Upload I-797 Copy #2", type=["pdf"], key="dual_2")

    if copy_1 and copy_2:
        c1_bytes = copy_1.read()
        c2_bytes = copy_2.read()
        
        c1_data = parse_i797_entities(c1_bytes)
        c2_data = parse_i797_entities(c2_bytes)
        
        st.markdown("### 📋 Side-by-Side Extracted Parameters")
        
        comp_table = [
            {"Parameter": "Beneficiary", "Document #1": c1_data["beneficiary"], "Document #2": c2_data["beneficiary"]},
            {"Parameter": "Petitioner (Employer)", "Document #1": c1_data["petitioner"], "Document #2": c2_data["petitioner"]},
            {"Parameter": "USCIS Receipt Number", "Document #1": c1_data["receipt"], "Document #2": c2_data["receipt"]},
            {"Parameter": "Validity Window", "Document #1": c1_data["dates"], "Document #2": c2_data["dates"]},
        ]
        st.table(comp_table)

        # Conflict Evaluation Engine
        conflicts = []
        is_fraud = False

        norm_pet1 = re.sub(r'[^a-zA-Z0-9]', '', c1_data["petitioner"]).lower()
        norm_pet2 = re.sub(r'[^a-zA-Z0-9]', '', c2_data["petitioner"]).lower()

        # Check 1: Identical Receipt Number, Different Employer -> Definitive Forgery
        if c1_data["receipt"] != "Not Isolated" and c1_data["receipt"] == c2_data["receipt"]:
            if norm_pet1 != norm_pet2 and norm_pet1 != "" and norm_pet2 != "":
                is_fraud = True
                conflicts.append(
                    f"CRITICAL IMMIGRATION FRAUD: Both copies share the exact same USCIS Receipt Number ({c1_data['receipt']}), "
                    f"but name completely different petitioners: '{c1_data['petitioner']}' vs. '{c2_data['petitioner']}'. "
                    "USCIS never issues the same receipt number to two distinct employers. At least one document is guaranteed to be a cloned forgery."
                )

        # Check 2: Identical Validity Window, Conflicting Employers
        if c1_data["dates"] != "Not Isolated" and c1_data["dates"] == c2_data["dates"]:
            if norm_pet1 != norm_pet2 and norm_pet1 != "" and norm_pet2 != "":
                conflicts.append(
                    f"SUSPICIOUS DUPLICATE: Both records share the exact same validity window ({c1_data['dates']}) with conflicting employer names. "
                    "This strongly indicates a modified template."
                )

        st.markdown("---")
        if is_fraud:
            st.error("🚨 **CROSS-AUDIT VERDICT: CONFIRMED DOCUMENT FORGERY / CLONING**", icon="🛑")
            for c in conflicts:
                st.html(f"<div class='detail-block' style='border-left: 4px solid #c00;'><div class='detail-title'>🛑 Fatal Integrity Breach</div><div class='detail-text'>{c}</div></div>")
        elif conflicts:
            st.warning("⚠️ **CROSS-AUDIT VERDICT: CONFLICTING DATA DETECTED**", icon="⚡")
            for c in conflicts:
                st.html(f"<div class='detail-block' style='border-left: 4px solid #FFA500;'><div class='detail-title'>⚠️ Parameter Conflict</div><div class='detail-text'>{c}</div></div>")
        else:
            st.success("🛡️ **CROSS-AUDIT VERDICT: NO RECEIPT/EMPLOYER DIVERGENCE FOUND** \n\nBoth records are logically consistent under USCIS filing architecture.", icon="✅")

# -------------------------------------------------------------
# MODE 2: SINGLE H-1B (I-797) FRAUD DETECTOR
# -------------------------------------------------------------
elif app_mode == "🛂 Single H-1B (I-797) Fraud Detector":
    st.subheader("H-1B (Form I-797) Fraud, Tamper & Structural Detector")
    st.caption("Screens digital vector layers, text spans, and image-pixel compression matrices to isolate modifications.")
    
    h1b_file = st.file_uploader("Upload H-1B Approval Notice (PDF)", type=["pdf"], key="single_h1b_uploader")

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
        return ImageEnhance.Brightness(ela_img).enhance(scale)

    def audit_h1b_single(file_bytes, ela_thresh):
        parsed = parse_i797_entities(file_bytes)
        
        audit = {
            "is_tampered": False,
            "receipt_number": parsed["receipt"],
            "receipt_valid": parsed["receipt_valid"],
            "validity_dates": parsed["dates"],
            "petitioner": parsed["petitioner"],
            "beneficiary": parsed["beneficiary"],
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
            audit["tamper_evidence"].append(f"Multiple Save Footprint: {len(eof_markers)} %%EOF markers detected. File was re-saved post-generation.")

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

        # 3. Hybrid Visual and Pixel Inspection
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")

            for page_num in range(len(doc)):
                page = doc[page_num]
                flagged_boxes = []

                # Render page to PIL image
                pix = page.get_pixmap(dpi=150)
                pil_img = Image.open(io.BytesIO(pix.tobytes("png")))
                width, height = pil_img.size

                # Pixel ELA Matrix
                ela_image = run_image_ela(pil_img)
                ela_gray = np.array(ela_image.convert('L'))

                grid_step = 25
                for y in range(0, height - grid_step, grid_step):
                    for x in range(0, width - grid_step, grid_step):
                        cell = ela_gray[y:y+grid_step, x:x+grid_step]
                        if np.mean(cell) > (100 - ela_thresh) and np.std(cell) > 15:
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
            result = audit_h1b_single(file_bytes, sensitivity)
            
        st.write("")
        
        if result["is_tampered"]:
            st.error(
                f"🚨 **H-1B VERDICT: MODIFICATIONS DETECTED** \n\n"
                f"Isolated {result['flagged_regions_count']} anomaly cluster(s). Threat Confidence: {min(result['risk_score'] + result['flagged_regions_count'] * 5, 100)}/100.",
                icon="🛑"
            )
        else:
            st.success("🛡️ **H-1B VERDICT: NO INTERNAL MODIFICATIONS DETECTED**", icon="✅")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Receipt Number**")
            badge = "h1b-pass" if result["receipt_valid"] else "h1b-fail"
            st.html(f"<span class='h1b-tag {badge}'>{'VALID' if result['receipt_valid'] else 'INVALID / MISSING'}</span>")
            st.code(result["receipt_number"])
        with col2:
            st.markdown("**Petitioner**")
            st.info(result["petitioner"])
        with col3:
            st.markdown("**Beneficiary**")
            st.info(result["beneficiary"])
        with col4:
            st.markdown("**Validity Window**")
            st.info(result["validity_dates"])

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
# MODE 3: BATCH FORENSIC ANALYZER
# -------------------------------------------------------------
elif app_mode == "🔍 Batch PDF Forensic Analyzer":
    st.subheader("Batch Forensic Analyzer")
    uploaded_files = st.file_uploader("Upload PDF documents", type=["pdf"], accept_multiple_files=True, key="batch_upload")
    
    if uploaded_files:
        summary_data = []
        for up_file in uploaded_files:
            b = up_file.read()
            eofs = len(re.findall(b'%%EOF', b))
            xrefs = len(re.findall(b'xref', b))
            verdict = "🛑 Red Flag" if eofs > 1 or xrefs > 1 else "✅ Clean"
            summary_data.append({"Filename": up_file.name, "Verdict": verdict, "Save Cycles": eofs, "XREF Maps": xrefs})
        st.dataframe(summary_data, use_container_width=True)

# -------------------------------------------------------------
# MODE 4: UNIVERSAL CONVERTER
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
# MODE 5: PRIVACY SANITIZER
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
