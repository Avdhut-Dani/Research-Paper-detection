import pymupdf
import os
import datetime

def generate_summary_page(data, output_path):
    """
    Generates a stylized one-page executive summary PDF using PyMuPDF.
    """
    try:
        doc = pymupdf.open()
        page = doc.new_page()
        
        # Colors (RGB normalized 0-1)
        bg_dark = (15/255, 23/255, 42/255)     # #0f172a
        accent_blue = (59/255, 130/255, 246/255) # #3b82f6
        accent_green = (16/255, 185/255, 129/255) # #10b981
        accent_red = (239/255, 68/255, 68/255)   # #ef4444
        accent_orange = (245/255, 158/255, 11/255) # #f59e0b
        text_white = (248/255, 250/255, 252/255)
        text_gray = (148/255, 163/255, 184/255)
        
        # Fill Background
        page.draw_rect(page.rect, color=bg_dark, fill=bg_dark)
        
        y = 50
        
        # Header
        page.insert_text((50, y), "EXECUTIVE SUMMARY", fontname="helv", fontsize=24, color=accent_blue, fontfile=None)
        y += 30
        page.insert_text((50, y), f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", fontname="helv", fontsize=10, color=text_gray)
        y += 40
        
        # Mode Badge
        mode = data.get("analysis_mode", "Unknown")
        page.draw_rect(pymupdf.Rect(50, y-15, 250, y+5), color=accent_blue, fill=accent_blue, width=0)
        page.insert_text((60, y), f"ANALYSIS MODE: {mode}", fontname="helv", fontsize=12, color=text_white)
        y += 50
        
        # Integrity Score Section
        score = data.get("integrity_score", 0.0)
        score_color = accent_green if score > 70 else (accent_orange if score > 40 else accent_red)
        
        page.insert_text((50, y), "INTEGRITY SCORE", fontname="helv", fontsize=14, color=text_gray)
        y += 40
        page.insert_text((50, y), f"{score:.2f}", fontname="helv", fontsize=48, color=score_color)
        y += 20
        
        # Breakdown
        breakdown = data.get("integrity_breakdown", {})
        if breakdown:
            y += 20
            page.insert_text((50, y), "BREAKDOWN:", fontname="helv", fontsize=12, color=text_white)
            y += 20
            for key, val in breakdown.items():
                label = key.replace("_", " ").title()
                symbol = "+" if "bonus" in key.lower() else "-"
                color = accent_green if symbol == "+" else accent_red
                page.insert_text((60, y), f"• {label}: {symbol}{val}", fontname="helv", fontsize=11, color=color)
                y += 18
        
        y += 30
        
        # Key Metrics Grid
        page.insert_text((50, y), "KEY METRICS", fontname="helv", fontsize=14, color=text_gray)
        y += 30
        metrics = [
            f"Claims Found: {data.get('claims', 0) + data.get('vague_claims', 0)}",
            f"Vague Claims: {data.get('vague_claims', 0)}",
            f"References: {data.get('total_citations_count', 0)}",
            f"Self-Citation Ratio: {(data.get('self_citation_ratio', 0) * 100):.1f}%"
        ]
        curr_y = y
        for i, m in enumerate(metrics):
            pos_x = 50 if i % 2 == 0 else 300
            page.insert_text((pos_x, curr_y), m, fontname="helv", fontsize=11, color=text_white)
            if i % 2 != 0: curr_y += 20
            
        y = curr_y + 40
        
        # System Review & Reasoning
        page.insert_text((50, y), "SYSTEM PEER-REVIEW & REASONING", fontname="helv", fontsize=14, color=text_gray)
        y += 30
        
        review = data.get("system_review", {"strengths": [], "weaknesses": [], "red_flags": []})
        
        # Combined list for display
        items = []
        for rf in review.get("red_flags", []): items.append(("🚩 CRITICAL", rf, accent_red))
        for w in review.get("weaknesses", []): items.append(("⚠️ WEAKNESS", w, accent_orange))
        for s in review.get("strengths", []): items.append(("✅ STRENGTH", s, accent_green))
        
        for label, content, color in items[:8]: # Limit to 8 for one page
            if isinstance(content, dict):
                text = content.get("text", "")
                source = content.get("source", "System")
            else:
                text = str(content)
                source = "System"
                
            page.insert_text((50, y), label, fontname="helv", fontsize=11, color=color)
            y += 16
            
            # Simple text wrapping for content
            wrapped_text = []
            words = text.split()
            line = ""
            for w_word in words:
                if len(line + w_word) < 90:
                    line += w_word + " "
                else:
                    wrapped_text.append(line)
                    line = w_word + " "
            wrapped_text.append(line)
            
            for line_text in wrapped_text[:2]: # Max 2 lines per point
                page.insert_text((60, y), line_text, fontname="helv", fontsize=10, color=text_white)
                y += 14
            
            page.insert_text((60, y), f"Source: {source}", fontname="helv", fontsize=8, color=text_gray)
            y += 20
            
            if y > 750: break # Page safety
            
        doc.save(output_path)
        doc.close()
        return output_path
        
    except Exception as e:
        print(f"Error generating summary page: {e}")
        return None
