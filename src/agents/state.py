from typing import List, Optional, TypedDict, Dict, Any
from pydantic import BaseModel, Field

class LeadSchema(BaseModel):
    domain: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    decision_maker_name: Optional[str] = None
    decision_maker_role: Optional[str] = None
    is_valid: bool = False
    validation_reason: Optional[str] = None
    score: float = 0.0
    score_breakdown: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    subject: Optional[str] = None
    body_html: Optional[str] = None

class AgentState(TypedDict):
    run_id: int
    icp_config: Dict[str, Any]
    queries: List[str]
    raw_leads: List[LeadSchema]
    enriched_leads: List[LeadSchema]
    validated_leads: List[LeadSchema]
    scored_leads: List[LeadSchema]
    final_leads: List[LeadSchema]
    error: Optional[str]
    dry_run: bool
