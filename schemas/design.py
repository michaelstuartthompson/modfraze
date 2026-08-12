"""
Schema for design generation and approval workflow.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DesignRequest:
    """Request to generate a design from a trend"""
    trend_id: int
    design_type: str = "graphic"  # graphic, text, hybrid
    style_prompt: Optional[str] = None  # Additional style instructions
    

@dataclass
class DesignResult:
    """Result of design generation"""
    trend_id: int
    prompt: str
    image_url: str
    mockup_url: Optional[str] = None
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()


@dataclass
class DesignApproval:
    """Design approval decision"""
    design_id: int
    approved: bool
    notes: Optional[str] = None
    approved_at: datetime = None
    
    def __post_init__(self):
        if self.approved_at is None:
            self.approved_at = datetime.utcnow()
