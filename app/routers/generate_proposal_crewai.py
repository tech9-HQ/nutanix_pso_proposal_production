from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal
import logging

# Import AI crew functions
from app.crewai.enhanced_crews import generate_proposal_with_qa, extract_sections_for_docx

# Import DOCX builders
from app.services.docx_builder import build_short_proposal_docx
from app.services.enhanced_toc import build_detailed_proposal_with_enhanced_toc

router = APIRouter(prefix="/api", tags=["proposal"])
log = logging.getLogger("proposal_router")


class ProposalRequest(BaseModel):
    customer_name: str
    industry: str
    deployment_type: Literal["on-premise", "remote", "hybrid", "dark-site"]
    proposal_type: Literal["short", "detailed"] = "detailed"
    hardware_choice: str
    client_requirements: str
    client_boq: str


@router.post("/generate_proposal")
async def generate_proposal(payload: ProposalRequest):
    try:
        log.info("=" * 80)
        log.info(f"Generating {payload.proposal_type.upper()} proposal for {payload.customer_name}")
        log.info("=" * 80)

        # ========================================================================
        # STEP 1: Generate proposal content using AI
        # ========================================================================
        log.info("Step 1: Calling AI to generate proposal content...")

        result = generate_proposal_with_qa(
            customer_name=payload.customer_name,
            industry=payload.industry,
            deployment_type=payload.deployment_type,
            proposal_type=payload.proposal_type,
            hardware_choice=payload.hardware_choice,
            client_requirements=payload.client_requirements,
            client_boq=payload.client_boq,
        )

        # ========================================================================
        # STEP 2: Extract sections for DOCX builder
        # ========================================================================
        log.info("Step 2: Extracting sections from AI output...")

        sections = extract_sections_for_docx(result)

        log.info(f"✓ AI generated {len(sections)} sections")
        log.debug(f"  Section keys: {list(sections.keys())}")

        # ========================================================================
        # STEP 3: Build DOCX
        # ========================================================================
        if payload.proposal_type == "detailed":
            log.info("Step 3: Building DETAILED proposal with enhanced TOC...")

            doc_bytes = build_detailed_proposal_with_enhanced_toc(sections)
            filename = f"{payload.customer_name}_nutanix_pso_detailed.docx".replace(" ", "_")

        else:
            log.info("Step 3: Building SHORT proposal...")

            narrative_sections = {
                "executive_summary": sections.get("executive_summary", ""),
                "scope_summary": sections.get("scope_summary", sections.get("scope_of_work_in_scope", "")),
                "key_benefits": sections.get("key_benefits", []),
                "risk_note": sections.get("risks_and_mitigation", ""),
                "closing": sections.get("closing", "Thank you for considering our proposal."),
            }

            services = _parse_services_from_boq(
                sections.get("commercial_boq_expanded", payload.client_boq)
            )

            file_path = build_short_proposal_docx(
                customer_name=payload.customer_name,
                industry=payload.industry,
                deployment_type=payload.deployment_type,
                proposal_type=payload.proposal_type,
                hardware_choice=payload.hardware_choice,
                client_requirements=payload.client_requirements,
                client_boq=payload.client_boq,
                services=services,
                narrative_sections=narrative_sections,
            )

            with open(file_path, "rb") as f:
                doc_bytes = f.read()

            filename = f"{payload.customer_name}_nutanix_pso_short.docx".replace(" ", "_")

        # ========================================================================
        # STEP 4: Return DOCX
        # ========================================================================
        log.info(f"Step 4: Returning document ({len(doc_bytes)} bytes)")

        return StreamingResponse(
            iter([doc_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
        )

    except Exception as e:
        import traceback
        log.error("Unhandled ERROR during proposal generation:")
        log.error(traceback.format_exc())
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"generate_proposal crashed: {e}")



def _parse_services_from_boq(boq_content: str) -> list:
    """
    Parse BOQ content into services list for short proposal.
    Extracts service names and man-days from BOQ text.
    
    Args:
        boq_content: Raw BOQ text with service items and man-days
        
    Returns:
        List of service dictionaries with name, category, duration, rate
    """
    import re
    
    log.debug("Parsing services from BOQ content...")
    
    services = []
    lines = [l.strip() for l in boq_content.splitlines() if l.strip()]
    
    for line in lines:
        # Skip total/summary lines
        if any(kw in line.lower() for kw in ["total", "subtotal", "grand total", "phase"]):
            continue
            
        # Extract man-days using multiple patterns
        man_days_match = re.search(r'(\d+)\s*(?:man[-\s]?days?|days?)', line, re.IGNORECASE)
        man_days = int(man_days_match.group(1)) if man_days_match else 5
        
        # Extract service description (before the arrow or colon)
        description = re.split(r'[→:(\[—-]{2,}|\t', line)[0].strip()
        description = re.sub(r'\s*\d+\s*$', '', description).strip()
        
        # Remove leading dashes or bullets
        description = re.sub(r'^[-*•]\s*', '', description)
        
        if description and len(description) > 3:
            # Categorize service based on keywords
            category = "General Services"
            desc_lower = description.lower()
            
            if any(kw in desc_lower for kw in ["assessment", "analyze", "review", "audit"]):
                category = "Assessment Services"
            elif any(kw in desc_lower for kw in ["migration", "move", "transfer", "cutover"]):
                category = "Migration Services"
            elif any(kw in desc_lower for kw in ["deploy", "implement", "install", "setup"]):
                category = "Deployment Services"
            elif any(kw in desc_lower for kw in ["develop", "custom", "integration", "build"]):
                category = "Development Services"
            elif any(kw in desc_lower for kw in ["test", "validation", "verify", "uat"]):
                category = "Testing Services"
            elif any(kw in desc_lower for kw in ["training", "knowledge", "documentation", "handover"]):
                category = "Training & Support"
            
            # Determine rate (workshops are higher)
            rate = 600 if "workshop" in desc_lower else 400
            
            services.append({
                "service_name": description,
                "category_name": category,
                "duration_days": man_days,
                "price_man_day": rate,
            })
            
            log.debug(f"  Parsed: {description} → {man_days} days ({category})")
    
    # If no services parsed, add default
    if not services:
        log.warning("No services parsed from BOQ, using default")
        services = [
            {
                "service_name": "Professional Services - Nutanix Implementation",
                "category_name": "General Services",
                "duration_days": 30,
                "price_man_day": 400,
            }
        ]
    
    log.info(f"✓ Parsed {len(services)} services from BOQ")
    return services