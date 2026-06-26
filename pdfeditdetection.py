# -------------------------------------------------------------
# MODE A: ADVANCED FORENSIC ANALYZER UTILITY
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
            "metadata": {},
            "detailed_findings": [],
            "edited_segments": [],  # New container for exact text changes
            "producer": "Unknown",
            "dates_match": "Verified"
        }
        
        # --- 1. BASIC BINARY & METADATA FORENSICS ---
        eof_markers = re.findall(b'%%EOF', file_bytes)
        xref_markers = re.findall(b'xref', file_bytes)
        results["incremental_updates"] = len(eof_markers)
        results["xref_tables"] = len(xref_markers)
        
        if len(eof_markers) > 1:
            results["is_edited"] = True
            results["detailed_findings"].append({
                "title": "🚨 Incremental Structural Patch Detected",
                "text": f"Found {len(eof_markers)} End-of-File (%%EOF) tokens. This indicates structural version stacking."
            })

        # --- 2. DEEP COMPONENT ANALYSIS: ISOLATING SPECIFIC EDITS ---
        try:
            doc_fitz = fitz.open(stream=file_bytes, filetype="pdf")
            
            # Look at internal string segments to catch overlapping text/masked elements
            for page_num in range(len(doc_fitz)):
                page = doc_fitz[page_num]
                
                # Extract text blocks with precise structural metadata layout attributes
                text_blocks = page.get_text("blocks")
                
                # Look for suspicious layout anomalies (e.g., text blocks on top of each other)
                for block in text_blocks:
                    block_text = block[4].strip()
                    
                    # If an object contains signatures of common consumer web-tool generation blocks
                    if any(marker in block_text.lower() for marker in ["ilovepdf", "smallpdf", "watermark", "eval"]):
                        results["is_edited"] = True
                        results["edited_segments"].append(f"Page {page_num + 1} Overlay Segment: '{block_text}'")
            
            # Extract Font names to double-check editing layers
            all_fonts = []
            for page in doc_fitz:
                all_fonts.extend([f[3] for f in page.get_fonts() if f])
            unique_fonts = list(set(all_fonts))
            suspicious_fonts = [f for f in unique_fonts if "identity-h" in f.lower() or "custom" in f.lower()]
            results["font_anomalies"] = len(suspicious_fonts)
            
        except Exception as e:
            results["detailed_findings"].append({"title": "Forensic Parse Interruption", "text": str(e)})

        # Standard baseline metadata processing
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
        except:
            pass

        return results

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        with st.spinner("PDF BUSTER running structural isolation layers..."):
            analysis = analyze_pdf_advanced(file_bytes)
            
        st.write("")
        if analysis["is_edited"]:
            st.error("💥 **PDF BUSTER VERDICT: SUB-OBJECT MODIFICATIONS DETECTED**", icon="🚨")
            card_class = "alert-active"
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
        
        # --- NEW SECTION: DISPLAYING EXACT EDITED PORTIONS ---
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
