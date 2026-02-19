import pymupdf

def highlight_text_in_pdf(pdf_path, highlights, output_path):
    """
    Highlights instances of text strings in a PDF with specific colors.
    
    Args:
        pdf_path (str): Path to the input PDF.
        highlights (list): List of (text, color_rgb) tuples. 
                           e.g., [("Claim text", (1, 1, 0)), ("Ref text", (0, 1, 0))]
        output_path (str): Path to save the highlighted PDF.
    """
    try:
        doc = pymupdf.open(pdf_path)
        
        for text, color in highlights:
            if not text or len(text) < 5:
                continue
                
            for page in doc:
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
