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
    """
    Represents a detailed technical analysis of the webpage.

    Attributes:
        Content_Discrepancies: Issues related to text/content.
        Styling_Discrepancies: Issues with visual styling or design.
        Intentional_Flaws_And_Known_Issues: Known/expected issues acknowledged in the webpage.
        Functional_Discrepancies: Issues related to the webpage’s behavior or logic.
    """
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
    """
    Evaluations performed using non-LLM tools (e.g., linters, validators).

    Attributes:
        Accessibility_Report: Accessibility audit report.
        Performance_Report: Performance-related observations.
        Validation_Report: W3C or markup validation issues.
        Layout_Report: Visual layout and structural issues.
    """
    Accessibility_Report: Optional[AccessibilityReport] = Field(default=None, alias="Accessibility Report")
    Performance_Report: Optional[PerformanceReport] = Field(default=None, alias="Performance Report")
    Validation_Report: Optional[ValidationReport] = Field(default=None, alias="Validation Report")
    Layout_Report: Optional[LayoutReport] = Field(default=None, alias="Layout Report")


class OtherIssue(BaseModel):
    """
    Represents miscellaneous issues not covered by main categories.

    Attributes:
        Issue: Description of the issue.
        Details: Additional context.
        Code: Related code snippet.
        Recommended_Fix: Suggested way to fix the problem.
    """
    Issue: Optional[str] = Field(default=None, alias="Issue")
    Details: Optional[str] = Field(default=None, alias="Details")
    Code: Optional[str] = Field(default=None, alias="Code")
    Recommended_Fix: Optional[str] = Field(default=None, alias="Recommended Fix")


class WebpageAnalysisResponse(BaseModel):
    """
    Root model for holding the entire analysis result of a webpage.

    Attributes:
        Executive_Summary: Brief summary of key findings.
        Detailed_Analysis: In-depth breakdown of issues (content, styling, etc.).
        Non_LLM_Evaluations: Results from automated tools (accessibility, performance, etc.).
        Other_Issues: Any other findings not captured by the categories above.

    Config:
        populate_by_name: Enables population of fields by their names in input data.
        alias_generator: Disabled (set to None).
        json_encoders: No custom JSON encoders defined.
    """
    Executive_Summary: Optional[str] = Field(default=None, alias="Executive Summary")
    Detailed_Analysis: Optional[DetailedAnalysis] = Field(default=None, alias="Detailed Analysis")
    Non_LLM_Evaluations: Optional[NonLLMEvaluations] = Field(default=None, alias="Non-LLM Evaluations")
    Other_Issues: List[OtherIssue] = Field(default_factory=list, alias="Other Issues")

    model_config = {
        "populate_by_name": True,
        "alias_generator": None,
        "json_encoders": {},
    }
