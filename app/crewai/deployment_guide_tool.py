# app/crewai/deployment_guide_tool.py
"""
Deployment Guide Tool - Provides Nutanix PSO service estimates
from your deployment guide PDF (converted to structured data)
"""

try:
    from crewai.tools import tool
except ImportError:
    from crewai_tools import tool
from typing import Dict, List, Optional
import logging

log = logging.getLogger(__name__)

# ============================================================================
# NUTANIX PSO SERVICES CATALOG
# Based on your deployment guide - UPDATE THESE WITH YOUR ACTUAL DATA
# ============================================================================

NUTANIX_SERVICES_CATALOG = {
    # Assessment Services (Discovery & Planning)
    "infrastructure_assessment": {
        "service_name": "Infrastructure Assessment",
        "category": "Assessment Services",
        "description": "Current state analysis of infrastructure, workloads, and dependencies",
        "duration_days": [3, 5],  # Min-max range
        "rate_usd_per_day": 600,
        "deliverables": [
            "Infrastructure inventory report",
            "Application dependency mapping",
            "Capacity analysis",
            "Gap analysis"
        ],
        "complexity_factors": {
            "multi_site": 1.2,
            "legacy_apps": 1.15,
            "large_scale": 1.25  # 500+ VMs
        }
    },
    
    "migration_planning_workshop": {
        "service_name": "Migration Planning Workshop",
        "category": "Assessment Services",
        "description": "Collaborative workshop to plan migration strategy and waves",
        "duration_days": [2, 3],
        "rate_usd_per_day": 600,
        "deliverables": [
            "Migration strategy document",
            "Wave-based migration plan",
            "Risk mitigation strategy",
            "Communication plan"
        ]
    },
    
    # Architecture & Design Services
    "architecture_design": {
        "service_name": "Solution Architecture & Design",
        "category": "Architecture Services",
        "description": "Detailed technical architecture for Nutanix implementation",
        "duration_days": [5, 8],
        "rate_usd_per_day": 600,
        "deliverables": [
            "Detailed architecture document",
            "Network design",
            "Storage design",
            "Security architecture",
            "DR/BC design"
        ],
        "complexity_factors": {
            "multi_site": 1.3,
            "hybrid_cloud": 1.2,
            "complex_networking": 1.15
        }
    },
    
    # Deployment Services
    "cluster_deployment": {
        "service_name": "Nutanix Cluster Deployment",
        "category": "Deployment Services",
        "description": "Physical installation and configuration of Nutanix clusters",
        "duration_days": [3, 5],  # Per cluster
        "rate_usd_per_day": 400,
        "deliverables": [
            "Cluster installation",
            "Network configuration",
            "Storage configuration",
            "Foundation imaging",
            "Initial validation"
        ],
        "notes": "Duration is per cluster. Add 2 days for each additional cluster."
    },
    
    "prism_configuration": {
        "service_name": "Prism Central & Management Setup",
        "category": "Deployment Services",
        "description": "Configure Prism Central for centralized management",
        "duration_days": [2, 3],
        "rate_usd_per_day": 400,
        "deliverables": [
            "Prism Central deployment",
            "Category configuration",
            "Role-based access control",
            "Alert and monitoring setup"
        ]
    },
    
    # Migration Services
    "vm_migration": {
        "service_name": "VM Migration (ESXi/Hyper-V to AHV)",
        "category": "Migration Services",
        "description": "Migrate VMs from existing hypervisor to Nutanix AHV",
        "duration_days_per_100vms": [8, 12],
        "rate_usd_per_day": 400,
        "deliverables": [
            "VM migration execution",
            "Application validation",
            "Performance validation",
            "Migration report"
        ],
        "complexity_factors": {
            "esxi_to_ahv": 1.25,
            "hyperv_to_ahv": 1.30,
            "legacy_os": 1.20,
            "custom_apps": 1.15
        },
        "notes": "Duration scales with VM count. Includes testing and validation."
    },
    
    "database_migration": {
        "service_name": "Database Migration (Nutanix Database Service)",
        "category": "Migration Services",
        "description": "Migrate databases to Nutanix Database Service (NDB)",
        "duration_days_per_db": [2, 4],
        "rate_usd_per_day": 600,
        "deliverables": [
            "Database migration",
            "Performance optimization",
            "NDB configuration",
            "Backup validation"
        ],
        "complexity_factors": {
            "oracle": 1.5,
            "sql_server": 1.2,
            "postgres": 1.0
        }
    },
    
    # Security & Compliance
    "security_hardening": {
        "service_name": "Security Hardening & Flow Configuration",
        "category": "Security Services",
        "description": "Implement security best practices and Flow microsegmentation",
        "duration_days": [2, 4],
        "rate_usd_per_day": 600,
        "deliverables": [
            "Security policy implementation",
            "Flow microsegmentation",
            "Security audit report",
            "Compliance documentation"
        ]
    },
    
    # DR & Backup Services
    "dr_setup": {
        "service_name": "Disaster Recovery Setup",
        "category": "DR/BC Services",
        "description": "Configure DR replication and failover procedures",
        "duration_days": [3, 5],
        "rate_usd_per_day": 400,
        "deliverables": [
            "DR site configuration",
            "Replication setup",
            "Failover procedures",
            "DR testing and validation"
        ]
    },
    
    "backup_configuration": {
        "service_name": "Backup & Recovery Configuration",
        "category": "DR/BC Services",
        "description": "Configure backup solutions (native or third-party)",
        "duration_days": [2, 3],
        "rate_usd_per_day": 400,
        "deliverables": [
            "Backup policy configuration",
            "Retention policy setup",
            "Recovery testing",
            "Backup documentation"
        ]
    },
    
    # Testing & Validation
    "testing_validation": {
        "service_name": "Testing & Validation",
        "category": "Quality Assurance",
        "description": "Comprehensive testing of migrated workloads",
        "duration_days": [5, 8],
        "rate_usd_per_day": 400,
        "deliverables": [
            "Test plan execution",
            "Performance benchmarking",
            "User acceptance testing",
            "Test report"
        ]
    },
    
    # Knowledge Transfer
    "knowledge_transfer": {
        "service_name": "Knowledge Transfer & Training",
        "category": "Training Services",
        "description": "Train customer team on Nutanix operations",
        "duration_days": [2, 3],
        "rate_usd_per_day": 600,
        "deliverables": [
            "Administrator training",
            "Operations documentation",
            "Runbooks",
            "Support handoff"
        ]
    },
    
    # Managed Services
    "managed_services_30days": {
        "service_name": "30-Day Hypercare Support",
        "category": "Managed Services",
        "description": "Post-migration support and monitoring",
        "duration_days": 30,
        "rate_usd_per_day": 200,  # Reduced rate for extended engagement
        "deliverables": [
            "Daily health checks",
            "Performance monitoring",
            "Issue resolution",
            "Weekly status reports"
        ]
    },
}

# ============================================================================
# SERVICE BUNDLES (Common packages)
# ============================================================================

SERVICE_BUNDLES = {
    "quick_start": {
        "bundle_name": "Nutanix Quick Start Package",
        "description": "Basic deployment for small environments",
        "included_services": [
            "infrastructure_assessment",
            "cluster_deployment",
            "knowledge_transfer"
        ],
        "total_duration_days": [8, 13],
        "typical_use_case": "POC or small production deployment (1 cluster, <100 VMs)"
    },
    
    "enterprise_migration": {
        "bundle_name": "Enterprise Migration Package",
        "description": "Comprehensive migration for large environments",
        "included_services": [
            "infrastructure_assessment",
            "migration_planning_workshop",
            "architecture_design",
            "cluster_deployment",
            "vm_migration",
            "security_hardening",
            "dr_setup",
            "testing_validation",
            "knowledge_transfer",
            "managed_services_30days"
        ],
        "total_duration_days": [45, 70],
        "typical_use_case": "Large-scale production migration (500+ VMs, multi-site)"
    },
    
    "hybrid_cloud": {
        "bundle_name": "Hybrid Cloud Implementation",
        "description": "On-premises + NC2 hybrid cloud setup",
        "included_services": [
            "infrastructure_assessment",
            "architecture_design",
            "cluster_deployment",
            "prism_configuration",
            "security_hardening",
            "testing_validation",
            "knowledge_transfer"
        ],
        "total_duration_days": [25, 35],
        "typical_use_case": "Hybrid cloud with NC2 on AWS/Azure"
    }
}


# ============================================================================
# TOOL FUNCTIONS
# ============================================================================

@tool("nutanix_service_lookup")
def nutanix_service_lookup(service_name_or_keyword: str) -> Dict:
    """
    Look up Nutanix PSO service details from deployment guide.
    
    Args:
        service_name_or_keyword: Service name or keyword to search for
            Examples: "migration", "assessment", "cluster deployment"
    
    Returns:
        Dictionary with service details including duration, cost, deliverables
    """
    search_term = service_name_or_keyword.lower()
    
    # Direct match
    if search_term in NUTANIX_SERVICES_CATALOG:
        service = NUTANIX_SERVICES_CATALOG[search_term]
        log.info(f"Found exact match for service: {search_term}")
        return {
            "found": True,
            "service": service,
            "service_key": search_term
        }
    
    # Keyword search
    matches = []
    for key, service in NUTANIX_SERVICES_CATALOG.items():
        if (search_term in key.lower() or 
            search_term in service["service_name"].lower() or
            search_term in service["description"].lower()):
            matches.append({
                "service_key": key,
                "service": service,
                "relevance": "high" if search_term in key else "medium"
            })
    
    if matches:
        log.info(f"Found {len(matches)} matches for keyword: {search_term}")
        return {
            "found": True,
            "matches": matches,
            "count": len(matches)
        }
    
    log.warning(f"No services found for: {search_term}")
    return {
        "found": False,
        "message": f"No services found matching '{service_name_or_keyword}'",
        "suggestion": "Try keywords like: migration, assessment, deployment, security"
    }


@tool("nutanix_bundle_lookup")
def nutanix_bundle_lookup(bundle_keyword: str) -> Dict:
    """
    Look up pre-packaged service bundles from deployment guide.
    
    Args:
        bundle_keyword: Bundle name or use case keyword
            Examples: "quick start", "enterprise", "hybrid cloud"
    
    Returns:
        Dictionary with bundle details and included services
    """
    search_term = bundle_keyword.lower()
    
    # Search bundles
    matches = []
    for key, bundle in SERVICE_BUNDLES.items():
        if (search_term in key.lower() or 
            search_term in bundle["bundle_name"].lower() or
            search_term in bundle["typical_use_case"].lower()):
            
            # Expand bundle with full service details
            services = []
            for service_key in bundle["included_services"]:
                if service_key in NUTANIX_SERVICES_CATALOG:
                    services.append(NUTANIX_SERVICES_CATALOG[service_key])
            
            matches.append({
                "bundle_key": key,
                "bundle_info": bundle,
                "services": services
            })
    
    if matches:
        log.info(f"Found {len(matches)} bundle matches for: {search_term}")
        return {
            "found": True,
            "bundles": matches,
            "count": len(matches)
        }
    
    return {
        "found": False,
        "message": f"No bundles found matching '{bundle_keyword}'",
        "available_bundles": list(SERVICE_BUNDLES.keys())
    }


@tool("calculate_migration_effort")
def calculate_migration_effort(
    vm_count: int,
    source_hypervisor: str = "vmware",
    has_databases: bool = False,
    database_count: int = 0,
    has_custom_apps: bool = False
) -> Dict:
    """
    Calculate estimated migration effort based on scope.
    
    Args:
        vm_count: Number of VMs to migrate
        source_hypervisor: Source platform (vmware, hyperv, physical)
        has_databases: Whether databases need migration
        database_count: Number of databases (if has_databases=True)
        has_custom_apps: Whether custom applications are involved
    
    Returns:
        Dictionary with effort estimates and breakdown
    """
    # Base VM migration effort
    vm_service = NUTANIX_SERVICES_CATALOG["vm_migration"]
    vms_per_hundred = vm_count / 100
    base_days = vm_service["duration_days_per_100vms"][1]  # Use max for conservative
    vm_days = vms_per_hundred * base_days
    
    # Apply complexity factors
    complexity = 1.0
    if source_hypervisor.lower() == "vmware":
        complexity *= vm_service["complexity_factors"]["esxi_to_ahv"]
    elif source_hypervisor.lower() == "hyperv":
        complexity *= vm_service["complexity_factors"]["hyperv_to_ahv"]
    
    if has_custom_apps:
        complexity *= vm_service["complexity_factors"]["custom_apps"]
    
    vm_days_adjusted = vm_days * complexity
    
    # Add database migration if needed
    db_days = 0
    if has_databases and database_count > 0:
        db_service = NUTANIX_SERVICES_CATALOG["database_migration"]
        db_days = database_count * db_service["duration_days_per_db"][1]
    
    total_migration_days = vm_days_adjusted + db_days
    
    return {
        "vm_count": vm_count,
        "vm_migration_days": round(vm_days_adjusted, 1),
        "database_migration_days": round(db_days, 1),
        "total_migration_days": round(total_migration_days, 1),
        "complexity_factor": round(complexity, 2),
        "breakdown": {
            "base_vm_days": round(vm_days, 1),
            "complexity_multiplier": round(complexity, 2),
            "database_days": round(db_days, 1)
        },
        "rate_usd_per_day": vm_service["rate_usd_per_day"],
        "estimated_cost_usd": round(total_migration_days * vm_service["rate_usd_per_day"], 2)
    }


# ============================================================================
# HELPER: Get All Services by Category
# ============================================================================

def get_services_by_category(category: str) -> List[Dict]:
    """Get all services in a specific category."""
    return [
        {**service, "service_key": key}
        for key, service in NUTANIX_SERVICES_CATALOG.items()
        if service["category"] == category
    ]


def get_all_categories() -> List[str]:
    """Get list of all service categories."""
    categories = set()
    for service in NUTANIX_SERVICES_CATALOG.values():
        categories.add(service["category"])
    return sorted(list(categories))


# Export tools for use in agents
__all__ = [
    'nutanix_service_lookup',
    'nutanix_bundle_lookup', 
    'calculate_migration_effort',
    'NUTANIX_SERVICES_CATALOG',
    'SERVICE_BUNDLES'
]