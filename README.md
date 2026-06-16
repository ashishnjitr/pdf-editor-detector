# pdf-editor-detector

import os

# Define the content for the README.md file
readme_content = """# 🔍 PDF Forensic Analyzer

An open-source, lightweight digital forensics tool built with Python to detect post-creation edits, metadata manipulation, and structural anomalies in PDF documents. 

Real-world PDF editors often leave behind digital "scars" when files are modified. This tool runs a multi-pass inspection to uncover hidden edit structures, timeline mismatches, and software signatures.

## 🚀 Live Demo
[Insert your deployed Streamlit URL here, e.g., https://your-app.streamlit.app]

---

## 🛠️ How It Works (Inspection Layers)

To reliably spot changes without false positives, the analyzer looks at the problem from three separate angles:

1. **Binary Structural Scan (`%%EOF` Markers)**
   Standard PDF generators compile a file with a single End-of-File marker. Most consumer PDF editors utilize "Incremental Saves," appending modifications to the end of the file without rewriting the core data. The tool counts these markers to identify post-creation tampering.
   
2. **Metadata Timeline Audit**
   Parses embedded metadata hashes to extract and compare `CreationDate` and `ModDate`. Any mismatch indicates the document structure was re-saved after its initial export.

3. **Application Signature Matching**
   Cross-references the `Producer` tag against a known signature matrix of web-based modifiers, consumer utilities, and white-out engines (e.g., iLovePDF, Canva, SmallPDF).

---

## ⚙️ Local Installation & Setup

If you want to run this project locally on your machine instead of using the cloud version, follow these steps:

### Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 1. Clone the Repository
