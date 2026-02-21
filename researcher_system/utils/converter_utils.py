import subprocess
import os
import logging

def convert_docx_to_pdf(docx_path, output_dir):
    """
    Converts a .docx file to .pdf using LibreOffice headless mode.
    Returns the path to the generated PDF.
    """
    try:
        # Command for LibreOffice headless conversion
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            docx_path
        ]
        
        logging.info(f"Converting {docx_path} to PDF in {output_dir}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Determine the output filename
        base_name = os.path.splitext(os.path.basename(docx_path))[0]
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            logging.error(f"PDF conversion failed: {result.stderr}")
            return None
            
    except Exception as e:
        logging.error(f"Error in DOCX to PDF conversion: {e}")
        return None
