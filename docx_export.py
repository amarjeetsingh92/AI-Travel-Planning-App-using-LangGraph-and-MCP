"""
Word Document (.docx) Export Module for Odyssey AI Travel Itineraries
Transforms multi-agent travel plans into elegantly formatted Microsoft Word documents.
"""

import io
import re
from datetime import datetime


def _add_styled_heading(doc, text: str, level: int = 1):
    """Add a styled heading with consistent branding colors."""
    from docx.shared import Pt, RGBColor
    h = doc.add_heading(level=level)
    run = h.add_run(text)
    run.font.name = "Calibri"
    if level == 1:
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = RGBColor(26, 54, 93)  # Deep Navy
    elif level == 2:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(43, 108, 176)  # Blue Accent
    else:
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(74, 85, 104)  # Slate
    return h


def _add_markdown_content(doc, markdown_text: str):
    """Parse common markdown constructs (headings, bullets, tables, paragraphs) into Word elements."""
    from docx.shared import Pt, RGBColor

    if not markdown_text or not markdown_text.strip():
        p = doc.add_paragraph("No additional details provided.")
        p.runs[0].font.italic = True
        p.runs[0].font.color.rgb = RGBColor(120, 120, 120)
        return

    lines = markdown_text.strip().split("\n")
    in_table = False
    table_lines = []

    def flush_table():
        nonlocal in_table, table_lines
        if not table_lines:
            return
        # Parse markdown table
        rows_data = []
        for tl in table_lines:
            if re.match(r"^\s*\|?\s*:?-+:?\s*\|", tl):
                continue  # skip separator line
            cells = [c.strip() for c in tl.strip().strip("|").split("|")]
            if cells:
                rows_data.append(cells)
        if rows_data:
            max_cols = max(len(r) for r in rows_data)
            t = doc.add_table(rows=len(rows_data), cols=max_cols)
            t.style = "Light Shading Accent 1" if "Light Shading Accent 1" in [s.name for s in doc.styles] else "Table Grid"
            for r_idx, row in enumerate(rows_data):
                for c_idx, cell_text in enumerate(row):
                    if c_idx < max_cols:
                        cell = t.cell(r_idx, c_idx)
                        cell.text = cell_text
                        if r_idx == 0:
                            for p in cell.paragraphs:
                                for run in p.runs:
                                    run.font.bold = True
                                    run.font.size = Pt(9.5)
                        else:
                            for p in cell.paragraphs:
                                for run in p.runs:
                                    run.font.size = Pt(9)
        table_lines = []
        in_table = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if in_table:
                flush_table()
            continue

        # Table detection
        if "|" in line and (line.startswith("|") or line.endswith("|") or " | " in line):
            in_table = True
            table_lines.append(line)
            continue
        elif in_table:
            flush_table()

        # Headings
        if line.startswith("### "):
            _add_styled_heading(doc, line.lstrip("#").strip(), level=3)
        elif line.startswith("## "):
            _add_styled_heading(doc, line.lstrip("#").strip(), level=2)
        elif line.startswith("# "):
            _add_styled_heading(doc, line.lstrip("#").strip(), level=1)
        elif line.startswith("---") or line.startswith("***"):
            # Separator
            p = doc.add_paragraph()
            p_border = p.add_run("―" * 40)
            p_border.font.color.rgb = RGBColor(200, 210, 225)
            p_border.font.size = Pt(8)
        elif line.startswith("- ") or line.startswith("* ") or line.startswith("• "):
            # Bullet point
            clean_text = line[2:].strip()
            p = doc.add_paragraph(style="List Bullet")
            _format_inline_markdown(p, clean_text)
        elif re.match(r"^\d+\.\s+", line):
            # Numbered list
            clean_text = re.sub(r"^\d+\.\s+", "", line)
            p = doc.add_paragraph(style="List Number")
            _format_inline_markdown(p, clean_text)
        else:
            # Normal paragraph
            p = doc.add_paragraph()
            _format_inline_markdown(p, line)

    if in_table:
        flush_table()


def _format_inline_markdown(paragraph, text: str):
    """Handle bold (**text**) and italic (*text*) inside paragraph runs."""
    from docx.shared import Pt, RGBColor
    
    # Tokenize by bold **
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.font.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(30, 41, 59)
        else:
            # Check for single italic *
            sub_parts = re.split(r"(\*.*?\*)", part)
            for sp in sub_parts:
                if sp.startswith("*") and sp.endswith("*") and len(sp) >= 2:
                    run = paragraph.add_run(sp[1:-1])
                    run.font.italic = True
                    run.font.name = "Calibri"
                    run.font.size = Pt(10.5)
                    run.font.color.rgb = RGBColor(51, 65, 85)
                else:
                    run = paragraph.add_run(sp)
                    run.font.name = "Calibri"
                    run.font.size = Pt(10.5)
                    run.font.color.rgb = RGBColor(51, 65, 85)


def generate_travel_plan_docx(plan_data: dict) -> bytes:
    """
    Generate a beautifully styled Microsoft Word (.docx) document from travel plan data.
    Returns bytes suitable for Streamlit st.download_button.
    """
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
    except ImportError:
        # Fallback if docx is unavailable
        text_content = f"# {plan_data.get('plan_title', 'Travel Plan')}\n\n"
        text_content += f"{plan_data.get('final_response', '')}\n\n"
        text_content += f"## Flights\n{plan_data.get('flight_results', '')}\n\n"
        text_content += f"## Stays\n{plan_data.get('hotel_results', '')}\n\n"
        text_content += f"## Weather\n{plan_data.get('weather_results', '')}\n\n"
        text_content += f"## Itinerary\n{plan_data.get('itinerary', '')}\n"
        return text_content.encode("utf-8")

    doc = docx.Document()

    # Standardize margins
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)

    # Header / Title Banner
    header_p = doc.add_paragraph()
    header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header_p.add_run("ODYSSEY AI · CURATED TRAVEL DOSSIER")
    header_run.font.name = "Calibri"
    header_run.font.size = Pt(20)
    header_run.font.bold = True
    header_run.font.color.rgb = RGBColor(26, 54, 93)

    title_text = plan_data.get("plan_title") or plan_data.get("destination") or "Custom Travel Itinerary"
    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = subtitle_p.add_run(f"Destination: {title_text}")
    sub_run.font.name = "Calibri"
    sub_run.font.size = Pt(13)
    sub_run.font.bold = True
    sub_run.font.color.rgb = RGBColor(214, 158, 46)  # Warm Gold Accent

    tagline_p = doc.add_paragraph()
    tagline_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tagline_run = tagline_p.add_run("Autonomous Multi-Agent Travel Intelligence · Verified Stays, Flights & Schedules")
    tagline_run.font.name = "Calibri"
    tagline_run.font.size = Pt(9.5)
    tagline_run.font.italic = True
    tagline_run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()

    # Metadata Table
    table = doc.add_table(rows=2, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Travel Style", "Trip Duration", "Preferred Currency", "Date Prepared"]
    values = [
        str(plan_data.get("style", "Curated")),
        f"{plan_data.get('duration', 'N/A')} Days" if plan_data.get("duration") else "Custom",
        str(plan_data.get("currency", "INR (₹)")),
        datetime.now().strftime("%B %d, %Y")
    ]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9)
        p.runs[0].font.color.rgb = RGBColor(26, 54, 93)

        val_cell = table.cell(1, c_idx)
        val_cell.text = values[c_idx]
        val_p = val_cell.paragraphs[0]
        val_p.runs[0].font.size = Pt(9.5)
        val_p.runs[0].font.color.rgb = RGBColor(51, 65, 85)

    doc.add_paragraph()

    # Section 1: Executive Summary & Concierge Advice
    _add_styled_heading(doc, "🌟 Executive Summary & Concierge Advice", level=1)
    final_resp = plan_data.get("final_response") or ""
    _add_markdown_content(doc, final_resp)

    doc.add_paragraph()

    # Section 2: Day-by-Day Itinerary
    itinerary_text = plan_data.get("itinerary") or ""
    if itinerary_text:
        _add_styled_heading(doc, "🗓️ Detailed Day-by-Day Itinerary", level=1)
        _add_markdown_content(doc, itinerary_text)
        doc.add_paragraph()

    # Section 3: Recommended Stays & Accommodations
    hotel_text = plan_data.get("hotel_results") or ""
    if hotel_text:
        _add_styled_heading(doc, "🏨 Recommended Stays & Accommodations", level=1)
        _add_markdown_content(doc, hotel_text)
        doc.add_paragraph()

    # Section 4: Flight & Transit Analysis
    flight_text = plan_data.get("flight_results") or ""
    if flight_text:
        _add_styled_heading(doc, "✈️ Flight & Transit Recommendations", level=1)
        _add_markdown_content(doc, flight_text)
        doc.add_paragraph()

    # Section 5: Weather & Climate Forecast
    weather_text = plan_data.get("weather_results") or ""
    if weather_text:
        _add_styled_heading(doc, "⛅ Climate, Forecast & Packing Recommendations", level=1)
        _add_markdown_content(doc, weather_text)
        doc.add_paragraph()

    # Footer note
    footer_p = doc.add_paragraph()
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_p.add_run("― Prepared exclusively by Odyssey AI · Autonomous Travel Planning System ―")
    footer_run.font.name = "Calibri"
    footer_run.font.size = Pt(8.5)
    footer_run.font.italic = True
    footer_run.font.color.rgb = RGBColor(148, 163, 184)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()
