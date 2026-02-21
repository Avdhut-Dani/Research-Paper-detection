import pymupdf
import os

def highlight_text_in_pdf(pdf_path, highlights, output_path):
    """
    Highlights instances of text strings in a PDF with specific colors.
    """
    try:
        doc = pymupdf.open(pdf_path)
        
        for text, color in highlights:
            if not text or len(text) < 5:
                continue
                
            for page in doc:
                # Use QUAD search for better precision in modern PDFs
                text_instances = page.search_for(text)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=color)
                    highlight.update()
                    
        doc.save(output_path)
        doc.close()
        return output_path
        
    except Exception as e:
        print(f"Error highlighting PDF: {e}")
        return None

def merge_pdfs(pdf_paths, output_path):
    """
    Merges multiple PDF files into one.
    """
    try:
        result_doc = pymupdf.open()
        for path in pdf_paths:
            if not path or not os.path.exists(path):
                continue
            with pymupdf.open(path) as sub_doc:
                result_doc.insert_pdf(sub_doc)
        
        result_doc.save(output_path)
        result_doc.close()
        return output_path
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return None
