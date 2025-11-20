# app/crewai/detailed_proposal_crew.py (UPDATED)
from __future__ import annotations
from typing import Any, Dict
import json

from .enhanced_crews import generate_proposal_with_qa, extract_sections_for_docx


def generate_detailed_proposal_sections(
    *,
    customer_name: str,
    industry: str,
    deployment_type: str,
    proposal_type: str,
    hardware_choice: str,
    client_requirements: str,
    client_boq: str,
) -> Dict[str, str]:
    """
    Run the detailed proposal crew and return cleaned sections for DOCX.

    This is a thin wrapper so the rest of the app doesn't need to know
    about CrewAI internals. It always forces `proposal_type="detailed"`.
    """
    # Run the detailed crew
    result: Dict[str, Any] = generate_proposal_with_qa(
        customer_name=customer_name,
        industry=industry,
        deployment_type=deployment_type,
        proposal_type="detailed",  # force detailed proposals here
        hardware_choice=hardware_choice,
        client_requirements=client_requirements,
        client_boq=client_boq,
        max_retries=1,
    )

    # Extract sections in the format docx_builder expects
    sections = extract_sections_for_docx(result)

    # Optional: log quality score if present (for debugging / tuning)
    qa_report = result.get("qa_report", {}) if isinstance(result, dict) else {}
    print(f"✓ Proposal generated | Quality: {qa_report.get('quality_score', 0)}/100")

    return sections
    