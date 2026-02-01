from pydantic import BaseModel, Field
from typing import List


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Job description text")


class AnalyzeResponse(BaseModel):
    requires_clearance: bool
    requires_citizenship: bool
    hits: List[str]
    evidence: List[str]
