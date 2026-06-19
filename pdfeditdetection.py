# 1. Install dependencies
!pip install pypdf -q

import io
import re
import pypdf
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

# Custom CSS for a beautiful modern dashboard theme
CSS_THEME = """
<style>
    .report-card { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; border-radius: 10px; margin-top: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .verdict-clean { background-color: #d4edda; border-left: 6px solid #28a745; color: #155724; }
    .verdict-warning { background-color: #fff3cd; border-left: 6px solid #ffc107; color: #856404; }
    .flag-item { margin: 8px 0; font-size: 14px; list-style-type: none; }
    .meta-table { width: 100%; border-collapse: collapse; margin-top: 15px; background: white; font-size: 13px; }
    .meta-table th, .meta-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    .meta-table th { background-color: #f8f9fa; font-weight: 600; }
</style>
"""

# Create interactive UI widgets
uploader = widgets.FileUpload(accept='.pdf', multiple=False, description="Upload PDF", button_style='primary')
output_area = widgets.Output()

def run_forensics(change):
    with output_area:
        clear_output()
        
        # Get uploaded file data safely
        uploaded_filename = list(uploader.value.keys())[0]
        file_bytes = uploader.value[uploaded_filename]['content']
        
        flags = []
        is_edited = False
        
        # 1. Binary Structural Scan
        eof_markers = re.findall(b'%%EOF', file_bytes)
        if len(eof_markers) > 1:
            is_edited = True
            flags.append(f"<strong>Incremental Saves Detected:</strong> Found {len(eof_markers)} file end-markers. A normal file usually has 1. This means changes were appended post-creation.")

        # 2. Extract and Parse Metadata
        cleaned_meta = {}
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            metadata = reader.metadata
            
            if metadata:
                cleaned_meta = {k.replace('/', ''): str(v) for k, v in metadata.items()}
                
                # Compare Dates
                create_date = cleaned_meta.get("CreationDate")
                mod_date = cleaned_meta.get("ModDate")
                if create_date and mod_date and (create_date != mod_date):
                    is_edited = True
                    flags.append("<strong>Timeline Anomaly:</strong> The Last Modification Date does not match the original Creation Date.")
                    
                # Identify suspicious consumer web-editors
                producer = cleaned_meta.get("Producer", "").lower()
                suspicious_tools = ["ilovepdf", "smallpdf", "pdf2go", "nitro", "soda", "libreoffice", "canva", "pdfescape"]
                for tool in suspicious_tools:
                    if tool in producer:
                        is_edited = True
                        flags.append(f"<strong>Editing Software Fingerprint:</strong> Document metadata flags usage of consumer utility tool: '<em>{cleaned_meta.get('Producer')}</em>'")
            else:
                is_edited = True
                flags.append("<strong>Stripped Structure:</strong> File contains zero metadata fields. High probability it was intentionally wiped or flattened.")
        except Exception as e:
            flags.append(f"<strong>Parsing Error:</strong> Could not read standard structural mapping ({str(e)}).")

        # --- HTML UI RENDERING ---
        display(HTML(CSS_THEME))
        
        # Layout container setup
        card_class = "verdict-warning" if is_edited else "verdict-clean"
        verdict_title = "⚠️ POTENTIAL MODIFICATIONS DETECTED" if is_edited else "✅ PASS: NO OBVIOUS MODIFICATIONS FOUND"
        
        html_report = f"""
        <div class="report-card {card_class}">
            <h2 style="margin-top:0;">{verdict_title}</h2>
            <p style="font-size: 14px;"><strong>Analyzed File:</strong> {uploaded_filename}</p>
            <hr style="border: 0; border-top: 1px solid rgba(0,0,0,0.1);">
        """
        
        if flags:
            html_report += "<h3>Forensic Flag Markers:</h3><ul>"
            for flag in flags:
                html_report += f"<li class='flag-item'>🚨 {flag}</li>"
            html_report += "</ul>"
        else:
            html_report += "<p>Structure, timelines, and application signatures look consistent with an unedited original document.</p>"
            
        html_report += "</div>"
        display(HTML(html_report))
        
        # Dropdown Accordion for Metadata Table
        if cleaned_meta:
            table_rows = "".join([f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>" for k, v in cleaned_meta.items()])
            metadata_html = f"""
            <table class="meta-table">
                <thead><tr><th>Metadata Field</th><th>Value</th></tr></thead>
                <tbody>{table_rows}<tr><td><strong>Total %%EOF Saves</strong></td><td>{len(eof_markers)}</td></tr></tbody>
            </table>
            """
            accordion = widgets.Accordion(children=[widgets.HTML(metadata_html)])
            accordion.set_title(0, '📊 View Extracted Technical Metadata Map')
            display(accordion)

# Link the uploader widget to our analysis framework
uploader.observe(run_forensics, names='value')

# Render components beautifully in Colab
print("🔽 DROP OR UPLOAD YOUR PDF FILE BELOW:")
display(uploader, output_area)
