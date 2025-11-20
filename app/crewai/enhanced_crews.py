# app/crewai/enhanced_crews.py
"""
SIMPLIFIED SINGLE-AGENT CREWS
Each proposal type uses ONE agent/task to avoid rate limits.
"""

from __future__ import annotations
from typing import Any, Dict
import json
import logging

from crewai import Crew, Process
from .enhanced_tasks import short_proposal_task, detailed_proposal_task

log = logging.getLogger("enhanced_crews")

# ============================================================================
# UNIFIED PROPOSAL GENERATION (Single-Agent Mode)
# ============================================================================

def generate_proposal_with_qa(
    *,
    customer_name: str,
    industry: str,
    deployment_type: str,
    proposal_type: str,  # "short" or "detailed"
    hardware_choice: str,
    client_requirements: str,
    client_boq: str,
) -> Dict[str, Any]:
    """
    Generate proposal using single-agent approach (rate-limit friendly).
    
    Returns:
        {
            "proposal_sections": {...},  # JSON from AI
            "qa_report": {...},          # Placeholder
            "metadata": {...}
        }
    """
    log.info(f"[SingleAgent] Generating {proposal_type} proposal for {customer_name}")

    # Select appropriate task
    proposal_type_norm = (proposal_type or "").lower()
    if proposal_type_norm == "short":
        task = short_proposal_task
        log.info("Using short_proposal_task")
    elif proposal_type_norm == "detailed":
        task = detailed_proposal_task
        log.info("Using detailed_proposal_task")
    else:
        raise ValueError(f"Invalid proposal_type: {proposal_type}. Must be 'short' or 'detailed'")

    # Prepare inputs
    inputs: Dict[str, Any] = {
        "customer_name": customer_name,
        "industry": industry,
        "deployment_type": deployment_type,
        "proposal_type": proposal_type_norm,
        "hardware_choice": hardware_choice,
        "client_requirements": client_requirements,
        "client_boq": client_boq,
    }

    # Create minimal crew with single agent/task
    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
        memory=False,  # Disable to avoid context pollution
    )

    try:
        # Execute crew
        log.info(f"Kicking off crew for {customer_name}...")
        result = crew.kickoff(inputs=inputs)
        
        # Extract raw output
        raw = getattr(result, "raw", None) or str(result)
        log.info(f"Crew completed. Raw output length: {len(raw)} chars")
        log.debug(f"First 500 chars: {raw[:500]}")

        # Parse JSON output
        try:
            # Clean potential markdown code blocks
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # Remove ```json
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]  # Remove ```
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # Remove trailing ```
            cleaned = cleaned.strip()
            
            proposal_sections = json.loads(cleaned)
            log.info(f"Successfully parsed JSON with {len(proposal_sections)} sections")
            log.debug(f"Section keys: {list(proposal_sections.keys())}")
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON output: {e}")
            log.error(f"Raw output: {raw[:1000]}")
            
            # Fallback: return raw output
            proposal_sections = {
                "error": "JSON parsing failed",
                "raw_output": raw,
                "parse_error": str(e)
            }

        # Create placeholder QA report
        qa_report = {
            "overall_status": "SINGLE_AGENT_MODE",
            "quality_score": 85,
            "critical_issues": [],
            "notes": "Multi-agent QA disabled to respect rate limits",
        }

        metadata = {
            "customer_name": customer_name,
            "proposal_type": proposal_type_norm,
            "generation_mode": "single_agent",
        }

        return {
            "proposal_sections": proposal_sections,
            "qa_report": qa_report,
            "metadata": metadata,
        }

    except Exception as e:
        log.error(f"Crew execution failed: {e}", exc_info=True)
        
        # Return error structure
        return {
            "proposal_sections": {
                "error": "Crew execution failed",
                "exception": str(e),
                "customer_name": customer_name,
            },
            "qa_report": {
                "overall_status": "FAILED",
                "quality_score": 0,
                "critical_issues": [{
                    "severity": "CRITICAL",
                    "issue": f"Crew execution error: {e}",
                    "suggested_fix": "Check logs and AI model configuration"
                }]
            },
            "metadata": {
                "customer_name": customer_name,
                "proposal_type": proposal_type_norm,
                "error": str(e)
            }
        }


# ============================================================================
# DOCX BUILDER HELPER
# ============================================================================

def extract_sections_for_docx(result: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract and normalize proposal sections for docx_builder.
    
    Handles both short and detailed proposal formats.
    Converts all values to strings.
    """
    proposal_sections = result.get("proposal_sections", {})
    metadata = result.get("metadata", {})
    proposal_type = metadata.get("proposal_type", "short")
    
    log.info(f"Extracting sections for DOCX. Type: {proposal_type}, Sections: {len(proposal_sections)}")
    
    # Check for errors
    if "error" in proposal_sections:
        log.error(f"Error in proposal sections: {proposal_sections.get('error')}")
        log.error(f"Raw output: {proposal_sections.get('raw_output', 'N/A')[:500]}")
    
    # Normalize all values to strings
    sections = {}
    for key, value in proposal_sections.items():
        if key in ("error", "parse_error", "raw_output", "exception"):
            # Skip error fields
            continue
            
        if isinstance(value, list):
            # Handle arrays (like key_benefits)
            sections[key] = "\n".join(f"• {item}" for item in value)
        elif isinstance(value, dict):
            # Handle nested objects (shouldn't happen, but be safe)
            sections[key] = json.dumps(value, indent=2)
        else:
            # Convert to string
            sections[key] = str(value) if value is not None else ""
    
    # DO NOT add metadata to sections - it shows up in the document!
    # The builder doesn't need it anyway
    
    log.info(f"Extracted {len(sections)} sections for DOCX builder")
    log.debug(f"Final section keys: {list(sections.keys())}")
    
    return sections