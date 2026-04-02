"""
Data models for the compliance audit environment.

Defines the structure of actions (what agents send) and observations 
(what the environment returns).
"""

from pydantic import BaseModel, Field


class ComplianceReward(BaseModel):
    """
    Reward for a compliance assessment action.
    
    The reward represents how well the agent identified violations
    and suggested fixes, scored from 0.0 (completely wrong) to 1.0 (perfect).
    """
    
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Score from 0.0 to 1.0 based on grading strategy (F1, partial credit, or composite)"
    )


class ComplianceAction(BaseModel):
    """
    An agent's compliance assessment of a document.
    
    The agent reviews a company document and identifies violations,
    explains the legal issues, and optionally suggests fixes.
    """
    
    violation_ids: list[str] = Field(
        description=(
            "List of rule IDs that are violated (e.g., ['RULE_01', 'RULE_03']). "
            "Only include rules that are genuinely violated."
        )
    )
    
    explanation: str = Field(
        description=(
            "Your legal reasoning. For each violation, explain which part of "
            "the document breaks the rule and why."
        )
    )
    
    suggested_rewrite: str = Field(
        description=(
            "For hard tasks: rewrite the violating sections to make them compliant. "
            "Should include specific retention periods, named third parties, "
            "explicit consent language, and clear user rights. "
            "Leave empty for easy and medium tasks."
        )
    )


class ComplianceObservation(BaseModel):
    """
    What the environment sends back after each action.
    
    Contains the document to review, the rulebook, and feedback
    from your previous attempt (if any).
    """
    
    doc_id: str = Field(
        description="Unique identifier for this document"
    )
    
    company_name: str = Field(
        description="Name of the company whose document you're reviewing"
    )
    
    document_text: str = Field(
        description="Full text of the privacy policy or data processing agreement"
    )
    
    rules_reference: str | dict = Field(
        description="The GDPR-style rulebook. Apply all rules to the document."
    )
    
    task_name: str = Field(
        description="Difficulty level: 'easy', 'medium', or 'hard'"
    )
    
    step_num: int = Field(
        description="Current step number (starts at 1 after reset)"
    )
    
    feedback: str = Field(
        description=(
            "Feedback from your previous attempt. Shows which violations you "
            "correctly identified, which you missed, and any false positives."
        )
    )
    
    previous_score: float = Field(
        description="Your score from the previous step (0.0 to 1.0)"
    )
