from typing import Optional
from pydantic import BaseModel

class ShortProposalRequest(BaseModel):
    customer_name: str
    industry: Optional[str] = None
    deployment_type: Optional[str] = None
    proposal_type: Optional[str] = "short"
    hardware_choice: Optional[str] = None
    client_requirements: Optional[str] = None
    client_boq: Optional[str] = None
