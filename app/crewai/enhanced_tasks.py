# app/crewai/enhanced_tasks.py - UPDATED WITH FIXES
"""
FIXED VERSION: Addresses all 4 issues
1. Better TOC instructions
2. WBS must be table
3. Commercial BOQ with proper breakdown
4. Timeline must be table
"""

from __future__ import annotations
from crewai import Task
from .enhanced_agents import (
    short_proposal_writer,
    detailed_proposal_writer,
)

# ============================================================================
# SHORT PROPOSAL TASK (UNCHANGED)
# ============================================================================

short_proposal_task = Task(
    description=(
        "Generate a complete short-form proposal (5-10 pages) with cost estimates.\n\n"
        "CUSTOMER CONTEXT:\n"
        "- Customer Name: {customer_name}\n"
        "- Industry: {industry}\n"
        "- Deployment Type: {deployment_type}\n"
        "- Hardware: {hardware_choice}\n\n"
        "CLIENT REQUIREMENTS:\n"
        "{client_requirements}\n\n"
        "CLIENT BOQ (Bill of Quantities):\n"
        "{client_boq}\n\n"
        "YOUR TASK:\n"
        "Analyze the requirements and generate a professional short proposal.\n\n"
        "OUTPUT FORMAT (CRITICAL):\n"
        "Return ONLY valid JSON with these 9 keys:\n"
        "{\n"
        '  "executive_summary": "text",\n'
        '  "scope_summary": "text",\n'
        '  "key_benefits": ["item1", "item2", "item3", "item4"],\n'
        '  "approach_overview": "text",\n'
        '  "scope_of_work_in_scope": "text",\n'
        '  "scope_of_work_out_of_scope": "text",\n'
        '  "commercial_boq_expanded": "Service 1 -> 5 days\\nService 2 -> 10 days\\n...",\n'
        '  "risks_and_mitigation": "text",\n'
        '  "closing": "text"\n'
        "}\n"
    ),
    agent=short_proposal_writer,
    expected_output="Valid JSON with 9 keys, customer-specific content",
)

# ============================================================================
# DETAILED PROPOSAL TASK (FIXED FOR ALL 4 ISSUES)
# ============================================================================

detailed_proposal_task = Task(
    description=(
        "Generate comprehensive detailed proposal with ALL 27 sections.\n\n"
        "CUSTOMER CONTEXT:\n"
        "- Customer Name: {customer_name}\n"
        "- Industry: {industry}\n"
        "- Deployment Type: {deployment_type}\n"
        "- Hardware: {hardware_choice}\n\n"
        "CLIENT REQUIREMENTS:\n"
        "{client_requirements}\n\n"
        "CLIENT BOQ:\n"
        "{client_boq}\n\n"
        "====================================================================\n"
        "CRITICAL FORMATTING REQUIREMENTS:\n"
        "====================================================================\n\n"
        "SECTION 14: WORK BREAKDOWN STRUCTURE (WBS)\n"
        "MUST be a markdown table with this EXACT format:\n\n"
        "| Phase | Task | Description | Duration (Days) | Dependencies |\n"
        "|-------|------|-------------|-----------------|-------------|\n"
        "| Phase 1: Assessment | Infrastructure Assessment | Review current VMware environment | 3 | Customer access provided |\n"
        "| Phase 1: Assessment | Requirements Workshop | Define success criteria | 2 | Stakeholder availability |\n"
        "| Phase 1: Assessment | Architecture Design | Design target Nutanix solution | 5 | Assessment complete |\n"
        "| Phase 2: Deployment | Cluster Deployment | Deploy Nutanix clusters | 10 | Hardware racked |\n"
        "| Phase 2: Deployment | Prism Central Setup | Install and configure PC | 5 | Cluster deployed |\n"
        "| Phase 2: Deployment | NCM Configuration | Setup Cloud Manager | 3 | Prism Central ready |\n"
        "| Phase 3: Migration | Wave 1 - Dev/Test | Migrate test VMs | 8 | Cluster validated |\n"
        "| Phase 3: Migration | Wave 2 - Production | Migrate prod VMs | 15 | Wave 1 complete |\n"
        "| Phase 3: Migration | Wave 3 - Critical | Migrate critical apps | 12 | Wave 2 complete |\n"
        "| Phase 4: Testing | Functional Testing | Test all applications | 5 | Migration complete |\n"
        "| Phase 4: Testing | Performance Testing | Benchmark performance | 3 | Functional tests pass |\n"
        "| Phase 4: Testing | UAT Support | User acceptance testing | 4 | Performance validated |\n"
        "| Phase 5: Handover | Knowledge Transfer | Train customer team | 3 | UAT complete |\n"
        "| Phase 5: Handover | Documentation | Deliver all documents | 2 | Training complete |\n"
        "| Phase 5: Handover | Hypercare Support | Post-go-live support | 10 | Production cutover |\n\n"
        "Include 15-20 tasks minimum across all phases.\n"
        "Each row must be a separate task with specific duration.\n\n"
        "====================================================================\n\n"
        "SECTION 25: COMMERCIAL BOQ - CRITICAL FORMAT\n"
        "You MUST create a detailed service breakdown with man-days.\n"
        "DO NOT return the client BOQ input. Generate NEW services.\n\n"
        "Format as plain text list (the builder will create the table):\n\n"
        "Phase 1: Assessment & Planning\n"
        "- Current State Infrastructure Assessment -> 5 man-days\n"
        "- Architecture Design Workshop -> 8 man-days\n"
        "- Migration Planning & Runbook Development -> 5 man-days\n\n"
        "Phase 2: Deployment & Configuration\n"
        "- Nutanix Cluster Deployment (3 clusters) -> 15 man-days\n"
        "- Prism Central Installation & Configuration -> 5 man-days\n"
        "- NCM Starter Setup -> 3 man-days\n"
        "- Network & Security Configuration -> 4 man-days\n\n"
        "Phase 3: Migration Execution\n"
        "- Migration Wave 1 (Dev/Test, 50 VMs) -> 8 man-days\n"
        "- Migration Wave 2 (Non-Critical Prod, 150 VMs) -> 15 man-days\n"
        "- Migration Wave 3 (Business-Critical, 200 VMs) -> 20 man-days\n"
        "- Migration Wave 4 (Mission-Critical 24x7) -> 12 man-days\n\n"
        "Phase 4: Testing & Validation\n"
        "- Functional Testing (per wave) -> 5 man-days\n"
        "- Performance Benchmarking -> 3 man-days\n"
        "- User Acceptance Testing Support -> 4 man-days\n\n"
        "Phase 5: Knowledge Transfer & Support\n"
        "- Knowledge Transfer Sessions (3 sessions) -> 3 man-days\n"
        "- Documentation Delivery -> 2 man-days\n"
        "- Post-Go-Live Hypercare (2 weeks) -> 10 man-days\n\n"
        "Project Management (throughout) -> 10 man-days\n\n"
        "IMPORTANT: Each line must have format 'Service name -> X man-days'\n"
        "Total should be 80-150 man-days depending on complexity.\n\n"
        "====================================================================\n\n"
        "SECTION 26: PROJECT TIMELINE\n"
        "Title must be 'Project Timeline & Milestones' (NOT Gantt Style).\n"
        "MUST be a markdown table:\n\n"
        "| Phase | Duration | Start | End | Key Milestones |\n"
        "|-------|----------|-------|-----|----------------|\n"
        "| Phase 1: Assessment & Planning | 3 weeks | Week 1 | Week 3 | Architecture approved, Migration plan signed off |\n"
        "| Phase 2: Infrastructure Deployment | 4 weeks | Week 4 | Week 7 | Clusters deployed, Prism Central operational, NCM configured |\n"
        "| Phase 3: Migration Wave 1 | 2 weeks | Week 8 | Week 9 | 50 dev/test VMs migrated, Process validated |\n"
        "| Phase 3: Migration Wave 2 | 3 weeks | Week 10 | Week 12 | 150 non-critical VMs migrated, Integrations tested |\n"
        "| Phase 3: Migration Wave 3 | 4 weeks | Week 13 | Week 16 | 200 business-critical VMs migrated, UAT completed |\n"
        "| Phase 3: Migration Wave 4 | 2 weeks | Week 17 | Week 18 | Mission-critical apps migrated, Final cutover |\n"
        "| Phase 4: Testing & Validation | 2 weeks | Week 19 | Week 20 | All tests passed, Performance validated |\n"
        "| Phase 5: Stabilization & Handover | 2 weeks | Week 21 | Week 22 | Knowledge transfer complete, Project closed |\n\n"
        "Total Duration: 22 weeks (5.5 months)\n"
        "Critical Path: Assessment -> Deployment -> Migration Wave 1-4 -> Testing -> Handover\n"
        "Contingency Buffer: 2 weeks built into schedule\n\n"
        "====================================================================\n\n"
        "OUTPUT FORMAT:\n"
        "Return ONLY valid JSON with exactly 27 keys. NO markdown code blocks.\n\n"
        "{\n"
        '  "cover_page": "string",\n'
        '  "executive_summary": "string",\n'
        '  "about_tech9labs": "string",\n'
        '  "customer_background_and_business_drivers": "string",\n'
        '  "current_infrastructure_assessment": "string",\n'
        '  "target_state_architecture": "string",\n'
        '  "migration_strategy_and_approach": "string",\n'
        '  "parallel_build_approach": "string",\n'
        '  "migration_waves": "string",\n'
        '  "rollback_strategy": "string",\n'
        '  "validation_strategy": "string",\n'
        '  "scope_of_work_in_scope": "string",\n'
        '  "scope_of_work_out_of_scope": "string",\n'
        '  "detailed_wbs": "MUST BE MARKDOWN TABLE as specified above",\n'
        '  "tools_and_technologies": "string",\n'
        '  "deployment_and_configuration_details": "string",\n'
        '  "testing_validation_and_acceptance": "string",\n'
        '  "project_deliverables": "string",\n'
        '  "project_governance": "string",\n'
        '  "raci_matrix": "string with markdown table",\n'
        '  "communication_plan": "string",\n'
        '  "escalation_matrix": "string with markdown table",\n'
        '  "assumptions_and_dependencies": "string",\n'
        '  "risks_and_mitigation": "string with markdown table",\n'
        '  "commercial_boq_expanded": "MUST BE SERVICE BREAKDOWN as specified above",\n'
        '  "project_timeline": "MUST BE MARKDOWN TABLE with title Project Timeline & Milestones",\n'
        '  "annexures": "string"\n'
        "}\n\n"
        "CRITICAL:\n"
        "- detailed_wbs MUST be markdown table with | separators\n"
        "- commercial_boq_expanded MUST list services with -> X man-days format\n"
        "- project_timeline MUST be markdown table, title 'Project Timeline & Milestones'\n"
        "- ALL sections must have substantial content\n"
        "- Customer name must appear 20+ times\n"
    ),
    agent=detailed_proposal_writer,
    expected_output=(
        "Valid JSON with 27 keys. WBS as markdown table. BOQ with service breakdown. "
        "Timeline as markdown table with correct title. All content customer-specific."
    ),
)