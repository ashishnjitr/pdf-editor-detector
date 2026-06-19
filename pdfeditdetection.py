import streamlit as st
import pypdf
import re
import io

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="PDF BUSTER // Document Integrity Core", 
    page_icon="💥", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Flattened UI CSS configuration to support Python 3.14 environments cleanly
STYLE_INJECTION = (
    "<style>"
    ".brand-title { font-family: 'Courier New', Courier, monospace; font-size: 40px; font-weight: 900; letter-spacing: -1px; color: #FF4B4B; margin-bottom: 0px; display: flex; align-items: center; gap: 10px; }"
    ".brand-tagline { color: #6c757d; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 30px; border-bottom: 2px solid #efefef; padding-bottom: 10px; }"
    "html[data-theme='dark'] .brand-tagline { border-bottom-color: #2d3139; }"
    ".buster-grid { display: flex; justify-content: space-between; gap: 15px; margin-top: 20px; margin-bottom: 25px; }"
    ".buster-card { background-color: #f8f9fa; border: 1px solid #e9ecef; border-top: 4px solid #6c757d; border-radius: 6px; padding: 18px; flex: 1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }"
    "html[data-theme='dark'] .buster-card { background-color: #1c1f26; border-color: #2d3139; }"
    ".buster-card.alert-active { border-top-color: #FF4B4B; }"
    ".buster-card.clean-active { border-top-color: #28a745; }"
    ".buster-val { font-size: 26px; font-weight: 800; font-family: monospace; margin-bottom: 4px; }"
    ".buster-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #6c757d; font-weight: 600; }"
    ".detail-block { padding: 15px; border-radius: 6px; background-color: #fafafa; border-left: 4px solid #007bd9; margin-bottom: 12px; }"
    "html[data-theme='dark'] .detail-block { background-color: #1e222b; }"
    ".detail-title { font-weight: 700; font-size: 15px; margin-bottom: 4px; color: #1f2937; }"
    "html[data-theme='dark'] .detail-title { color: #f3f4f6; }"
    ".detail-text { font-size: 13.5px; color: #4b5563; line-height: 1.5; }"
    "html[data-theme='dark'] .detail-text { color: #d1d5db; }"
    "</style>"
)

st.markdown(STYLE_INJECTION, unsafe_with_html=True)

# 2. Rebranded Header Layout
st.markdown('<div class="brand-title">💥 PDF BUSTER</div>', unsafe_with_html=True)
st.markdown('<div class="brand-tagline">Automated Digital Tampering & Forensic Isolation Engine</div>', unsafe_with_html=True)

# Drag and Drop File Interface
uploaded_file = st.file_uploader("Drop target document here for structural analysis", type="pdf", label_visibility="visible")

def analyze_pdf(file_bytes):
    results = {
        "incremental_updates": 0,
        "is_edited": False,
        "metadata": {},
        "detailed_findings": [],
        "producer": "Unknown / System Generated",
        "dates_match": "Verified",
        "structure_status": "Secure"
    }
    
    # --- PHASE 1: BINARY STRUCTURE ANALYSIS ---
    eof_markers = re.findall(b'%%EOF', file_bytes)
    results["incremental_updates"] = len(eof_markers)
    
    if len(eof_markers) > 1:
        results["is_edited"] = True
        results["structure_status"] = "Compromised"
        results["detailed_findings"].append({
            "title": "Incremental Save Signature Isolated",
            "text": f"PDF BUSTER detected {len(eof_markers)} distinct End-Of-File (%%EOF) binary markers. Clean, unedited system exports write exactly 1 marker. Multiple markers explicitly indicate that an external editor appended content modifications to the original file container rather than rewriting it cleanly."
        })
    else:
        results["detailed_findings"].append({
            "title": "Binary Structure Integrity",
            "text": "File contains exactly 1 %%EOF token. The physical layout matches a native standalone structural compilation with no appended post-save revisions."
        })

    # --- PHASE 2: METADATA & TIMELINE AUDIT ---
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        metadata = reader.metadata
        
        if metadata:
            cleaned_meta = {k.replace('/', ''): str(v) for k, v in metadata.items()}
            results["metadata"] = cleaned_meta
            
            # Map values to interface metrics safely
            raw_producer = cleaned_meta.get("Producer", "Unknown")
            results["producer"] = raw_producer[:20] + "..." if len(raw_producer) > 20 else raw_producer
            
            create_date = cleaned_meta.get("CreationDate")
            mod_date = cleaned_meta.get("ModDate")
            
            if create_date and mod_date:
                if create_date != mod_date:
                    results["is_edited"] = True
                    results["dates_match"] = "Mismatch"
                    results["detailed_findings"].append({
                        "title": "Timeline Synchronization Failure",
                        "text": f"The document metadata reveals a chronological conflict. **Creation Date:** `{create_date}` does not align with the **Modification Date:** `{mod_date}`. This signifies that an environment wrapper updated the document metadata tree at a later instance."
                    })
                else:
                    results["detailed_findings"].append({
                        "title": "Metadata Chronology Aligned",
                        "text": f"Creation and modification timestamps are perfectly unified (`{create_date}`). Document has not undergone subsequent save loops since initial compilation."
                    })
            else:
                results["dates_match"] = "Stripped"
                results["detailed_findings"].append({
                    "title": "Incomplete Timeline Map",
                    "text": "Timestamps are missing or partially omitted from the header table. This occurs when privacy scrubbers or compression tools clear out standard tracking identifiers."
                })

            # --- PHASE 3: SOFTWARE FINGERPRINT CHECK ---
            producer_lower = raw_producer.lower()
            suspicious_tools = ["ilovepdf", "smallpdf", "pdf2go", "nitro", "soda", "libreoffice", "canva", "pdfescape", "sejda"]
            matched_tool = None
            for tool in suspicious_tools:
                if tool in producer_lower:
                    matched_tool = tool
                    break
                    
            if matched_tool:
                results["is_edited"] = True
                results["detailed_findings"].append({
                    "title": f"Application Fingerprint Traced: {matched_tool.upper()}",
                    "text": f"The document's Producer tag is stamped with *'{raw_producer}'*. This engine profile belongs to public-facing consumer editing utilities used frequently for text replacement, white-outs, or graphic overlays."
                })
        else:
            results["is_edited"] = True
            results["dates_match"] = "Wiped"
            results["producer"] = "None"
            results["structure_status"] = "Anomalous"
            results["detailed_findings"].append({
                "title": "Anomalous Container: Blank Object Dictionary",
                "text": "PDF BUSTER discovered that the metadata lookup dictionary is entirely empty. Standard automated enterprise systems populate this with structural indices. A completely blank state suggests intentional flattening or metadata wiping tools were run to erase editing histories."
            })
            
    except Exception as e:
        results["detailed_findings"].append({
            "title": "Parsing Interruption",
            "text": f"The tool encountered a reading hurdle while mapping the dictionary layout: {str(e)}."
        })

    return results

# 3. Dynamic Execution UI State
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    with st.spinner("PDF BUSTER running structural isolation layers..."):
        analysis = analyze_pdf(file_bytes)
        
    st.markdown("<br>", unsafe_with_html=True)
    
    # Rebranded High-Impact Verdict Banner
    if analysis["is_edited"]:
        st.error("💥 **PDF BUSTER VERDICT: DOCUMENT MODIFICATIONS ISOLATED**", icon="🚨")
        card_class = "alert-active"
    else:
        st.success("🛡️ **PDF BUSTER VERDICT: SECURE / NO MANIPULATION DETECTED**", icon="✅")
        card_class = "clean-active"
        
    # HTML Layout for Metric Cards
    metrics_html = (
        f'<div class="buster-grid">'
        f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["incremental_updates"]}</div><div class="buster-lbl">Save Cycles</div></div>'
        f'<div class="buster-card {card_class}"><div class="buster-val">{analysis["dates_match"]}</div><div class="buster-lbl">Timeline Sync</div></div>'
        f'<div class="buster-card {card_class}"><div class="buster-val" style="font-size:13px; padding-top:10px; overflow:hidden;">{analysis["producer"]}</div><div class="buster-lbl">Core Engine</div></div>'
        f'</div>'
    )
    st.markdown(metrics_html, unsafe_with_html=True)
    
    # Detailed High-Definition Forensic Output
    st.subheader("📋 Detailed Forensic Breakdown")
    st.caption("Granular breakdown of isolated binary layers and metadata validation checks:")
    
    for finding in analysis["detailed_findings"]:
        finding_html = (
            f'<div class="detail-block">'
            f'<div class="detail-title">🔹 {finding["title"]}</div>'
            f'<div class="detail-text">{finding["text"]}</div>'
            f'</div>'
        )
        st.markdown(finding_html, unsafe_with_html=True)
        
    # Technical Raw Matrix Accordion
    st.markdown("<br>", unsafe_with_html=True)
    with st.expander("🛠️ View Raw System Object Array"):
        if analysis["metadata"]:
            st.json(analysis["metadata"])
        else:
            st.caption("No standard object dictionary data available to extract.")
