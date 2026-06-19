import streamlit as st
import pypdf
import re
import io

# Set page configuration
st.set_page_config(page_title="PDF Forensics Tool", page_icon="🔍", layout="centered")

st.title("🔍 PDF Modification Detector")
st.write("Upload a PDF document to analyze its structure and metadata for signs of editing.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

def analyze_pdf(file_bytes):
    results = {
        "incremental_updates": 0,
        "is_edited": False,
        "metadata": {},
        "flags": []
    }
    
    # 1. Check for Incremental Updates (Binary Scan)
    eof_markers = re.findall(b'%%EOF', file_bytes)
    results["incremental_updates"] = len(eof_markers)
    
    if len(eof_markers) > 1:
        results["is_edited"] = True
        results["flags"].append(f"Multiple file versions detected ({len(eof_markers)} saves). This strongly indicates post-creation editing.")

    # 2. Parse Metadata using pypdf
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        metadata = reader.metadata
        
        if metadata:
            cleaned_meta = {k.replace('/', ''): str(v) for k, v in metadata.items()}
            results["metadata"] = cleaned_meta
            
            # Check Creation vs Modification Dates
            create_date = cleaned_meta.get("CreationDate")
            mod_date = cleaned_meta.get("ModDate")
            
            if create_date and mod_date and (create_date != mod_date):
                results["is_edited"] = True
                results["flags"].append("The Modification Date does not match the Creation Date.")
                
            # Check suspicious producers
            producer = cleaned_meta.get("Producer", "").lower()
            suspicious_tools = ["ilovepdf", "smallpdf", "pdf2go", "nitro", "soda", "libreoffice", "canva", "pdfescape"]
            for tool in suspicious_tools:
                if tool in producer:
                    results["is_edited"] = True
                    results["flags"].append(f"Document was processed by a known consumer editing tool: '{cleaned_meta.get('Producer')}'")
        else:
            results["is_edited"] = True
            results["flags"].append("No metadata found. The file may have been flattened or stripped to hide its history.")
            
    except Exception as e:
        results["flags"].append(f"Error parsing metadata: {str(e)}")

    return results

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    
    with st.spinner("Analyzing document structure..."):
        analysis = analyze_pdf(file_bytes)
        
    st.divider()
    
    # Display Verdict
    if analysis["is_edited"]:
        st.error("⚠️ Summary: Potential Modifications Detected")
    else:
        st.success("✅ Summary: No Obvious Modifications Detected")
        
    # Display Found Flags
    st.subheader("Analysis Findings")
    if analysis["flags"]:
        for flag in analysis["flags"]:
            st.markdown(f"* {flag}")
    else:
        st.write("No typical editing footprints or anomalies were found in the file structure.")
        
    # Technical Details Dropdown (Native Streamlit expander)
    with st.expander("View Raw Metadata & Structural Info"):
        st.write(f"**Total %%EOF Markers:** {analysis['incremental_updates']}")
        if analysis["metadata"]:
            st.json(analysis["metadata"])
        else:
            st.write("Metadata is completely empty.")
