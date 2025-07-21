from pydantic import BaseModel, Field
from typing import List, Optional


class ContentFinding(BaseModel):
    Section: Optional[str] = Field(default=None, alias="Section")
    Issue: Optional[str] = Field(default=None, alias="Issue")
    Details: Optional[str] = Field(default=None, alias="Details")
    Code: Optional[str] = Field(default=None, alias="Code")
    Recommended_Fix: Optional[str] = Field(default=None, alias="Recommended Fix")


class ContentDiscrepancy(BaseModel):
    Summary: Optional[str] = Field(default=None, alias="Summary")
    Findings: List[ContentFinding] = Field(default_factory=list, alias="Findings")


class StylingDiscrepancy(ContentDiscrepancy):
    pass


class IntentionalFinding(BaseModel):
    Category: Optional[str] = Field(default=None, alias="Category")
    Issue: Optional[str] = Field(default=None, alias="Issue")
    Details: Optional[str] = Field(default=None, alias="Details")
    Recommended_Fix: Optional[str] = Field(default=None, alias="Recommended Fix")


class IntentionalFlawsAndKnownIssues(BaseModel):
    Summary: Optional[str] = Field(default=None, alias="Summary")
    Findings: List[IntentionalFinding] = Field(default_factory=list, alias="Findings")


class FunctionalFinding(BaseModel):
    Issue: Optional[str] = Field(default=None, alias="Issue")
    Details: Optional[str] = Field(default=None, alias="Details")
    Code: Optional[str] = Field(default=None, alias="Code")
    Recommended_Fix: Optional[str] = Field(default=None, alias="Recommended Fix")


class FunctionalDiscrepancy(BaseModel):
    Summary: Optional[str] = Field(default=None, alias="Summary")
    Findings: List[FunctionalFinding] = Field(default_factory=list, alias="Findings")


class DetailedAnalysis(BaseModel):
    Content_Discrepancies: Optional[ContentDiscrepancy] = Field(default=None, alias="Content Discrepancies")
    Styling_Discrepancies: Optional[StylingDiscrepancy] = Field(default=None, alias="Styling Discrepancies")
    Intentional_Flaws_And_Known_Issues: Optional[IntentionalFlawsAndKnownIssues] = Field(
        default=None, alias="Intentional Flaws And Known Issues"
    )
    Functional_Discrepancies: Optional[FunctionalDiscrepancy] = Field(default=None, alias="Functional Discrepancies")


class KeyFinding(BaseModel):
    Issue: Optional[str] = Field(default=None, alias="Issue")
    Recommended_Fix: Optional[str] = Field(default=None, alias="Recommended Fix")


class AccessibilityReport(BaseModel):
    Summary: Optional[str] = Field(default=None, alias="Summary")
    Key_Findings: List[KeyFinding] = Field(default_factory=list, alias="Key Findings")


class PerformanceReport(AccessibilityReport):
    pass


class ValidationReport(AccessibilityReport):
    pass


class LayoutReport(BaseModel):
    Summary: Optional[str] = Field(default=None, alias="Summary")
    Recommended_Fix: Optional[str] = Field(default=None, alias="Recommended Fix")


class NonLLMEvaluations(BaseModel):
    Accessibility_Report: Optional[AccessibilityReport] = Field(default=None, alias="Accessibility Report")
    Performance_Report: Optional[PerformanceReport] = Field(default=None, alias="Performance Report")
    Validation_Report: Optional[ValidationReport] = Field(default=None, alias="Validation Report")
    Layout_Report: Optional[LayoutReport] = Field(default=None, alias="Layout Report")


class OtherIssue(BaseModel):
    Issue: Optional[str] = Field(default=None, alias="Issue")
    Details: Optional[str] = Field(default=None, alias="Details")
    Code: Optional[str] = Field(default=None, alias="Code")
    Recommended_Fix: Optional[str] = Field(default=None, alias="Recommended Fix")


class WebpageAnalysisResponse(BaseModel):
    Executive_Summary: Optional[str] = Field(default=None, alias="Executive Summary")
    Detailed_Analysis: Optional[DetailedAnalysis] = Field(default=None, alias="Detailed Analysis")
    Non_LLM_Evaluations: Optional[NonLLMEvaluations] = Field(default=None, alias="Non-LLM Evaluations")
    Other_Issues: List[OtherIssue] = Field(default_factory=list, alias="Other Issues")

    model_config = {
        "populate_by_name": True,
        "alias_generator": None,
        "json_encoders": {},
    }
