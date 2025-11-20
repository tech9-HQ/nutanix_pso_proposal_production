"""
Enhanced Table of Contents for Detailed Proposals
Adds smart categorization, professional formatting, and page number references
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from typing import List, Tuple, Dict
import io
import logging


def build_detailed_proposal_with_enhanced_toc(sections: Dict[str, str]) -> bytes:
    """
    Build detailed proposal with enhanced TOC.
    """
    log = logging.getLogger("enhanced_toc_builder")
    log.info("="*80)
    log.info("BUILDING DETAILED PROPOSAL WITH ENHANCED TOC")
    log.info("="*80)
    
    # Clean sections: remove metadata keys
    cleaned_sections = {}
    metadata_keys = {
        "_metadata", "_proposal_type", "metadata", "proposal_type", 
        "qa_report", "debug_info", "error", "parse_error", "raw_output", 
        "exception", "final_answer"
    }
    
    for key, value in sections.items():
        if key not in metadata_keys:
            cleaned_sections[key] = value
        else:
            log.info(f"Filtered out metadata key: {key}")
    
    sections = cleaned_sections
    log.info(f"Cleaned sections: {len(sections)} sections")
    
    doc = Document()
    
    # Import from docx_builder
    from app.services.docx_builder import (
        apply_base_styles,
        add_branding,
        fetch_exchange_rate,
        add_commercial_boq_section,
    )
    
    apply_base_styles(doc)
    add_branding(doc)
    
    # ==================================================================
    # COVER PAGE
    # ==================================================================
    log.info("Adding cover page...")
    cover_text = sections.get("cover_page", "")
    customer_name = "Customer"
    
    # Extract customer name
    if "BirlaSoft" in str(sections.values()):
        customer_name = "BirlaSoft Limited"
    elif "customer_name" in cover_text.lower():
        import re
        match = re.search(r"customer[:\s]+([^\n]+)", cover_text, re.IGNORECASE)
        if match:
            customer_name = match.group(1).strip()
    
    # Simple cover page
    heading = doc.add_heading("Nutanix Professional Services Proposal", level=0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)
    
    sub_para = doc.add_paragraph()
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_para.add_run(f"Prepared for: {customer_name}")
    sub_run.bold = True
    sub_run.font.size = Pt(18)
    sub_run.font.color.rgb = RGBColor(0, 102, 204)
    
    doc.add_page_break()
    
    # ==================================================================
    # TABLE OF CONTENTS - CRITICAL!
    # ==================================================================
    log.info("Adding enhanced table of contents...")
    
    # Make sure this function exists and is called!
    try:
        add_enhanced_table_of_contents(doc)
        log.info("✓ TOC added successfully")
    except Exception as e:
        log.error(f"✗ Failed to add TOC: {e}")
        # Add simple fallback TOC
        doc.add_heading("Table of Contents", level=1)
        doc.add_paragraph("Table of contents will be generated when opened in Microsoft Word.")
        doc.add_paragraph("Right-click and select 'Update Field'.")
        doc.add_page_break()
    
    # ==================================================================
    # CONTENT SECTIONS
    # ==================================================================
    hierarchy = get_section_hierarchy()
    
    # Get ordered sections
    section_order = []
    for _, _, subsections in DETAILED_PROPOSAL_STRUCTURE:
        for section_key, _ in subsections:
            if section_key != "cover_page":
                section_order.append(section_key)
    
    log.info(f"Will add {len(section_order)} content sections")
    
    # Fetch exchange rate once
    exchange_rate = fetch_exchange_rate()
    
    # Add all sections
    for idx, section_key in enumerate(section_order):
        content = sections.get(section_key, "")
        if not content or not content.strip():
            log.warning(f"⚠ Missing content for: {section_key}")
            continue
        
        # Get display title
        title = None
        for _, _, subsections in DETAILED_PROPOSAL_STRUCTURE:
            for key, section_title in subsections:
                if key == section_key:
                    title = section_title
                    break
            if title:
                break
        
        if not title:
            title = section_key.replace("_", " ").title()
        
        is_last = (idx == len(section_order) - 1)
        
        # Special handling for BOQ
        if section_key == "commercial_boq_expanded":
            cat_num, sub_num = hierarchy.get(section_key, (7, 1))
            if sub_num == 1:
                cat_heading = doc.add_heading("7. Commercial & Timeline", level=1)
                cat_heading.paragraph_format.space_before = Pt(18)
                cat_heading.paragraph_format.page_break_before = True
            
            log.info(f"Adding BOQ section: {len(content)} chars")
            add_commercial_boq_section(
                doc,
                title,
                content,
                exchange_rate=exchange_rate,
                heading_level=2,
            )
        else:
            add_section_with_smart_heading(
                doc,
                section_key,
                title,
                content,
                hierarchy,
                add_page_break=not is_last,
            )
        
        log.info(f"✓ Added section {idx+1}/{len(section_order)}: {title}")
    
    # ==================================================================
    # SAVE TO BYTES
    # ==================================================================
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    log.info("="*80)
    log.info("✓ DETAILED PROPOSAL BUILD COMPLETE")
    log.info("="*80)
    
    return buffer.read()

# ============================================================================
# SMART SECTION GROUPING & CATEGORIZATION
# ============================================================================

# Professional categorization of all 26 sections
DETAILED_PROPOSAL_STRUCTURE: List[Tuple[str, str, List[Tuple[str, str]]]] = [
    (
        "1", 
        "Executive Overview",
        [
            ("cover_page", "Cover Page"),
            ("executive_summary", "Executive Summary"),
            ("about_tech9labs", "About Integrated Tech9 Labs"),
        ]
    ),
    (
        "2",
        "Customer Context & Requirements",
        [
            ("customer_background_and_business_drivers", "Customer Background & Business Drivers"),
            ("current_infrastructure_assessment", "Current Infrastructure Assessment"),
        ]
    ),
    (
        "3",
        "Technical Solution Architecture",
        [
            ("target_state_architecture", "Target State Architecture"),
            ("migration_strategy_and_approach", "Migration Strategy & Approach"),
            ("parallel_build_approach", "Parallel Build Methodology"),
            ("migration_waves", "Wave-Based Migration Plan"),
            ("rollback_strategy", "Rollback & Contingency Strategy"),
            ("validation_strategy", "Validation & Testing Strategy"),
        ]
    ),
    (
        "4",
        "Scope of Work & Deliverables",
        [
            ("scope_of_work_in_scope", "In-Scope Activities"),
            ("scope_of_work_out_of_scope", "Out-of-Scope Items"),
            ("detailed_wbs", "Work Breakdown Structure (WBS)"),
            ("tools_and_technologies", "Tools & Technologies"),
            ("deployment_and_configuration_details", "Deployment & Configuration Details"),
            ("testing_validation_and_acceptance", "Testing, Validation & Acceptance Criteria"),
            ("project_deliverables", "Project Deliverables"),
        ]
    ),
    (
        "5",
        "Project Governance & Management",
        [
            ("project_governance", "Governance Framework"),
            ("raci_matrix", "RACI Matrix"),
            ("communication_plan", "Communication Plan"),
            ("escalation_matrix", "Escalation Procedures"),
        ]
    ),
    (
        "6",
        "Risk Management & Dependencies",
        [
            ("assumptions_and_dependencies", "Assumptions & Dependencies"),
            ("risks_and_mitigation", "Risk Register & Mitigation Strategies"),
        ]
    ),
    (
        "7",
        "Commercial & Timeline",
        [
            ("commercial_boq_expanded", "Commercial Bill of Quantities"),
            ("project_timeline", "Project Timeline & Milestones"),
        ]
    ),
    (
        "8",
        "Annexures & References",
        [
            ("annexures", "Annexures & Supporting Documentation"),
        ]
    ),
]


def add_enhanced_table_of_contents(doc: Document) -> None:
    """
    Add a professional, categorized Table of Contents with automatic page numbering.
    
    Features:
    - Smart section grouping (8 major categories)
    - Hierarchical structure (Category → Sections)
    - Automatic page number references
    - Professional formatting with colors and spacing
    - Click-to-navigate hyperlinks (in Word)
    """
    
    # Title page
    toc_title = doc.add_heading("Table of Contents", level=0)
    toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in toc_title.runs:
        run.font.size = Pt(20)
        run.font.color.rgb = RGBColor(0, 51, 102)
        run.bold = True
    
    doc.add_paragraph()  # Spacing
    
    # Add instructional note
    note = doc.add_paragraph()
    note_run = note.add_run(
        "This proposal is organized into 8 major sections covering strategy, "
        "technical solution, project delivery, and commercials. "
        "Click any section title to navigate directly."
    )
    note_run.font.size = Pt(10)
    note_run.italic = True
    note_run.font.color.rgb = RGBColor(100, 100, 100)
    
    doc.add_paragraph()  # Spacing
    
    # Add manual TOC structure (pretty, hierarchical)
    for section_num, category_name, subsections in DETAILED_PROPOSAL_STRUCTURE:
        # Category heading (Level 1) - Bold, larger, colored
        category_para = doc.add_paragraph()
        category_para.paragraph_format.space_before = Pt(12)
        category_para.paragraph_format.space_after = Pt(6)
        category_para.paragraph_format.left_indent = Inches(0)
        
        category_run = category_para.add_run(f"{section_num}. {category_name}")
        category_run.bold = True
        category_run.font.size = Pt(13)
        category_run.font.color.rgb = RGBColor(0, 51, 102)
        
        # Subsections (Level 2) - Indented, normal weight
        for idx, (section_key, section_title) in enumerate(subsections, start=1):
            subsection_para = doc.add_paragraph()
            subsection_para.paragraph_format.left_indent = Inches(0.3)
            subsection_para.paragraph_format.space_before = Pt(2)
            subsection_para.paragraph_format.space_after = Pt(2)
            
            # Add section number
            num_run = subsection_para.add_run(f"{section_num}.{idx} ")
            num_run.font.size = Pt(11)
            num_run.font.color.rgb = RGBColor(68, 68, 68)
            
            # Add section title
            title_run = subsection_para.add_run(section_title)
            title_run.font.size = Pt(11)
            
            # Add leader dots
            leader_run = subsection_para.add_run(" " + "." * 80)
            leader_run.font.color.rgb = RGBColor(200, 200, 200)
            leader_run.font.size = Pt(9)
            
            # Add page number placeholder
            page_run = subsection_para.add_run(" XX")
            page_run.font.size = Pt(11)
            page_run.font.color.rgb = RGBColor(68, 68, 68)
    
    doc.add_paragraph()  # Spacing
    
    # Add Word TOC field for automatic page numbers
    # This creates the real TOC that Word will populate
    doc.add_paragraph()
    
    info_para = doc.add_paragraph()
    info_run = info_para.add_run(
        "Note: After opening in Microsoft Word, right-click the table below "
        "and select 'Update Field' to populate accurate page numbers."
    )
    info_run.font.size = Pt(9)
    info_run.italic = True
    info_run.font.color.rgb = RGBColor(100, 100, 100)
    
    # Insert Word TOC field
    toc_para = doc.add_paragraph()
    toc_run = toc_para.add_run()
    
    # Create TOC field XML
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    toc_run._r.append(fld_char_begin)
    
    # TOC instruction: show headings 1-3, hyperlinks, page numbers
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = r'TOC \o "1-3" \h \z \u'
    toc_run._r.append(instr_text)
    
    fld_char_separate = OxmlElement("w:fldChar")
    fld_char_separate.set(qn("w:fldCharType"), "separate")
    toc_run._r.append(fld_char_separate)
    
    # Placeholder text (will be replaced when field updates)
    toc_run._r.append(OxmlElement("w:t"))
    toc_run._r[-1].text = "[Automatic Table of Contents - Update this field in Word]"
    
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    toc_run._r.append(fld_char_end)
    
    doc.add_page_break()


def get_section_hierarchy() -> Dict[str, Tuple[int, int]]:
    """
    Return a mapping of section_key → (category_num, section_num) for heading levels.
    This ensures proper hierarchy in the document.
    
    Returns:
        Dict like {"executive_summary": (1, 2), ...}
        Where (1, 2) means Category 1, Section 2
    """
    hierarchy = {}
    
    for cat_idx, (section_num, category_name, subsections) in enumerate(DETAILED_PROPOSAL_STRUCTURE, start=1):
        for sub_idx, (section_key, section_title) in enumerate(subsections, start=1):
            hierarchy[section_key] = (cat_idx, sub_idx)
    
    return hierarchy


def add_section_with_smart_heading(
    doc: Document,
    section_key: str,
    title: str,
    content: str,
    hierarchy: Dict[str, Tuple[int, int]],
    add_page_break: bool = True,
) -> None:
    """
    Add a section with smart heading levels for proper TOC generation.
    
    Args:
        doc: Document object
        section_key: Section identifier (e.g., "executive_summary")
        title: Display title
        content: Section content
        hierarchy: Section hierarchy mapping
        add_page_break: Whether to add page break after section
    """
    from docx.shared import Pt
    
    # Determine heading level based on hierarchy
    if section_key in hierarchy:
        cat_num, sub_num = hierarchy[section_key]
        
        # Check if this is first section in category
        is_category_start = sub_num == 1
        
        if is_category_start:
            # Add category heading (Heading 1)
            category_title = None
            for section_num, cat_name, subsections in DETAILED_PROPOSAL_STRUCTURE:
                if subsections[0][0] == section_key:
                    category_title = f"{section_num}. {cat_name}"
                    break
            
            if category_title:
                cat_heading = doc.add_heading(category_title, level=1)
                cat_heading.paragraph_format.space_before = Pt(18)
                cat_heading.paragraph_format.space_after = Pt(12)
                cat_heading.paragraph_format.page_break_before = True
        
        # Add section heading (Heading 2)
        section_heading = doc.add_heading(title, level=2)
        section_heading.paragraph_format.space_before = Pt(12)
        section_heading.paragraph_format.space_after = Pt(6)
    else:
        # Fallback for sections not in hierarchy
        doc.add_heading(title, level=2)
    
    # Add content
    if content and content.strip():
        # Import here to avoid circular dependency
        import re
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        # Handle markdown tables
        lines = [l.rstrip() for l in content.splitlines()]
        if any(line.startswith("|") for line in lines):
            # Render as table (using existing logic from docx_builder)
            from app.services.docx_builder import add_block_as_paragraphs
            add_block_as_paragraphs(doc, content)
        else:
            # Split into paragraphs
            blocks = re.split(r"\n\s*\n", content)
            for block in blocks:
                block = block.strip()
                if block:
                    from app.services.docx_builder import add_block_as_paragraphs
                    add_block_as_paragraphs(doc, block)
    
    if add_page_break:
        doc.add_page_break()


# ============================================================================
# INTEGRATION FUNCTION FOR docx_builder.py
# ============================================================================

def build_detailed_proposal_with_enhanced_toc(sections: Dict[str, str]) -> bytes:
    """
    Build detailed proposal with enhanced TOC.
    This is a replacement for the existing build_detailed_proposal_docx function.
    
    Args:
        sections: Dictionary of section content
        
    Returns:
        DOCX file as bytes
    """
    import io
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    import logging
    
    log = logging.getLogger("enhanced_toc_builder")
    log.info("Building detailed proposal with enhanced TOC...")
    
    # Clean sections: remove metadata keys that shouldn't be in the document
    cleaned_sections = {}
    metadata_keys = {"_metadata", "_proposal_type", "metadata", "proposal_type", "qa_report", "debug_info", "error", "parse_error", "raw_output"}
    
    for key, value in sections.items():
        if key not in metadata_keys:
            cleaned_sections[key] = value
    
    sections = cleaned_sections
    log.info(f"Cleaned sections: {len(sections)} sections (removed metadata)")
    
    doc = Document()
    
    # Import necessary functions from docx_builder
    from app.services.docx_builder import (
        apply_base_styles,
        add_branding,
        fetch_exchange_rate,
        add_commercial_boq_section,
        RGBColor,
        Pt,
    )
    
    apply_base_styles(doc)
    add_branding(doc)
    
    # Cover page
    cover_text = sections.get("cover_page", "")
    customer_name = "Customer"
    
    if cover_text:
        # Simple cover page
        heading = doc.add_heading("Nutanix Professional Services Proposal", level=0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in heading.runs:
            run.font.color.rgb = RGBColor(0, 51, 102)
        
        # Try to extract customer name from cover_page or executive_summary
        if "BirlaSoft" in cover_text or "BirlaSoft" in sections.get("executive_summary", ""):
            customer_name = "BirlaSoft Limited"
        elif "Customer:" in cover_text:
            import re
            match = re.search(r"Customer:\s*(.+?)(?:\n|$)", cover_text)
            if match:
                customer_name = match.group(1).strip()
        
        sub_para = doc.add_paragraph()
        sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_run = sub_para.add_run(f"Prepared for: {customer_name}")
        sub_run.bold = True
        sub_run.font.size = Pt(18)
        sub_run.font.color.rgb = RGBColor(0, 102, 204)
        
        doc.add_page_break()
    
    # Enhanced Table of Contents
    add_enhanced_table_of_contents(doc)
    
    # Get section hierarchy
    hierarchy = get_section_hierarchy()
    
    # Get all sections in proper order
    section_order = []
    for _, _, subsections in DETAILED_PROPOSAL_STRUCTURE:
        for section_key, _ in subsections:
            if section_key != "cover_page":  # Already added
                section_order.append(section_key)
    
    # Fetch exchange rate once
    exchange_rate = fetch_exchange_rate()
    
    # Add all sections with smart headings
    for idx, section_key in enumerate(section_order):
        content = sections.get(section_key, "")
        if not content or not content.strip():
            log.warning(f"Missing or empty content for section: {section_key}")
            continue
        
        # Get display title
        title = None
        for _, _, subsections in DETAILED_PROPOSAL_STRUCTURE:
            for key, section_title in subsections:
                if key == section_key:
                    title = section_title
                    break
            if title:
                break
        
        if not title:
            title = section_key.replace("_", " ").title()
        
        is_last = (idx == len(section_order) - 1)
        
        # Special handling for commercial BOQ
        if section_key == "commercial_boq_expanded":
            # Add category heading if needed
            cat_num, sub_num = hierarchy.get(section_key, (7, 1))
            if sub_num == 1:
                cat_heading = doc.add_heading("7. Commercial & Timeline", level=1)
                cat_heading.paragraph_format.space_before = Pt(18)
                cat_heading.paragraph_format.page_break_before = True
            
            add_commercial_boq_section(
                doc,
                title,
                content,
                exchange_rate=exchange_rate,
                heading_level=2,
            )
            log.info(f"Added BOQ section: {title}")
        else:
            add_section_with_smart_heading(
                doc,
                section_key,
                title,
                content,
                hierarchy,
                add_page_break=not is_last,
            )
            log.info(f"Added section: {title}")
    
    # Save to bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    log.info("Detailed proposal with enhanced TOC built successfully")
    return buffer.read()


def build_detailed_proposal_with_enhanced_toc_OLD(sections: Dict[str, str]) -> bytes:
    """
    Build detailed proposal with enhanced TOC.
    This is a replacement for the existing build_detailed_proposal_docx function.
    
    Args:
        sections: Dictionary of section content
        
    Returns:
        DOCX file as bytes
    """
    import io
    from docx import Document
    from docx.shared import Pt
    from app.services.docx_builder import (
        apply_base_styles,
        add_branding,
        parse_cover_page_text,
        guess_customer_from_sections,
        fetch_exchange_rate,
        add_commercial_boq_section,
    )
    
    import logging
    log = logging.getLogger("enhanced_toc_builder")
    
    log.info("Building detailed proposal with enhanced TOC...")
    
    doc = Document()
    apply_base_styles(doc)
    
    # Cover page
    cover_text = sections.get("cover_page", "")
    if cover_text:
        project_title, customer_name, prepared_by, contents_items = parse_cover_page_text(cover_text)
        
        if not customer_name:
            customer_name = guess_customer_from_sections(sections)
        
        # Add cover page manually (simplified)
        add_branding(doc)
        
        heading = doc.add_heading("Nutanix Professional Services Proposal", level=0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in heading.runs:
            run.font.color.rgb = RGBColor(0, 51, 102)
        
        if customer_name:
            sub_para = doc.add_paragraph()
            sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sub_run = sub_para.add_run(f"Prepared for: {customer_name}")
            sub_run.bold = True
            sub_run.font.size = Pt(18)
        
        doc.add_page_break()
    
    # Enhanced Table of Contents
    add_enhanced_table_of_contents(doc)
    
    # Get section hierarchy
    hierarchy = get_section_hierarchy()
    
    # Get all sections in proper order
    section_order = []
    for _, _, subsections in DETAILED_PROPOSAL_STRUCTURE:
        for section_key, _ in subsections:
            if section_key != "cover_page":  # Already added
                section_order.append(section_key)
    
    # Add all sections with smart headings
    exchange_rate = fetch_exchange_rate()
    
    for idx, section_key in enumerate(section_order):
        content = sections.get(section_key, "")
        if not content:
            log.warning(f"Missing content for section: {section_key}")
            continue
        
        # Get display title
        title = None
        for _, _, subsections in DETAILED_PROPOSAL_STRUCTURE:
            for key, section_title in subsections:
                if key == section_key:
                    title = section_title
                    break
            if title:
                break
        
        if not title:
            title = section_key.replace("_", " ").title()
        
        is_last = (idx == len(section_order) - 1)
        
        # Special handling for commercial BOQ
        if section_key == "commercial_boq_expanded":
            # Add category heading if needed
            cat_num, sub_num = hierarchy.get(section_key, (7, 1))
            if sub_num == 1:
                cat_heading = doc.add_heading("7. Commercial & Timeline", level=1)
                cat_heading.paragraph_format.space_before = Pt(18)
                cat_heading.paragraph_format.page_break_before = True
            
            add_commercial_boq_section(
                doc,
                title,
                content,
                exchange_rate=exchange_rate,
                heading_level=2,
            )
            log.info(f"Added section: {title} (BOQ)")
        else:
            add_section_with_smart_heading(
                doc,
                section_key,
                title,
                content,
                hierarchy,
                add_page_break=not is_last,
            )
            log.info(f"Added section: {title}")
    
    # Save to bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    log.info("Detailed proposal with enhanced TOC built successfully")
    return buffer.read()