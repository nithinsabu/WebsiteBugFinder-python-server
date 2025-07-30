"""
This FastAPI application provides an endpoint for webpage UI analysis using a Gemini LLM model.

- Accepts HTML content, optional specifications, design file (image), and structured audit results.
- Constructs a detailed LLM prompt and optionally uploads an image for multimodal input.
- Returns structured feedback in a strict JSON schema defined by `WebpageAnalysisResponse`.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Annotated
import os
from app.gemini_client import get_client
from dotenv import load_dotenv
import random
import string
import json
import logging
from .models import WebpageAnalysisResponse
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
model = os.getenv("MODEL")
app = FastAPI()

# Load Gemini client
client = get_client()

def get_prompt(htmlText: str, specification: str | None = "", designFile: bool = False, webAuditResults: str = "") -> str:
    """
    Generates a formatted prompt string for a language model to perform a structured UI analysis.

    This function constructs a detailed instruction string that includes:
    - An example JSON response format for the model to strictly follow.
    - Provided HTML content to be analyzed.
    - Optional design specifications and flags for attached design files.
    - Optional non-LLM evaluation data (e.g., accessibility, performance, validation results).

    Args:
        htmlText (str): The raw HTML content to be analyzed.
        specification (str | None, optional): Optional design or functional specifications. Defaults to "".
        designFile (bool, optional): Indicates whether a design file is attached. Defaults to False.
        webAuditResults (str, optional): A JSON string containing non-LLM evaluation results. Expected keys:
            - "axeCoreResult"
            - "pageSpeedResult"
            - "nuValidatorResult"
            - "responsivenessResult"

    Returns:
        str: A formatted prompt string that includes all inputs and instructions for LLM-based analysis.

    Notes:
        - Ensures the output instructs the LLM to produce only raw JSON (no markdown, no surrounding text).
        - Embeds optional evaluation summaries in the prompt if present.
        - If evaluations are missing or invalid, the "Non-LLM Evaluations" field is marked as null.
    """
    try:
        evaluations = json.loads(webAuditResults) if webAuditResults else {}
    except json.JSONDecodeError:
        evaluations = {}

    prompt = (
        "Please perform a comprehensive UI analysis of the html mentioned and generate STRICTLY a JSON report "
        "(No additional text except the JSON response: Start with \"{\", end with \"}\". No markdown. Raw JSON as text.). The output must strictly follow the JSON structure provided "
        "in the 'Example Output Format' section below. Fill in the data based on my inputs, ensuring no deviation "
        "from the provided keys, nesting, or data types. Fill key \"code\" with the affected html code only. Fill the key \"Non-LLM Evaluations\" as null if input non-LLM Evaluations are not given (\"Non-LLM Evaluations\": null). If any key is inapplicable, fill it as null if the corresponding value is an object, fill it as [] (empty array) if corresponding value is an array.\n\n"
        "We are only concerned with a desktop screen analysis.\n\n"
        "**Example Output Format:**\n\n"
        '''{
  "Executive Summary": "...",
  "Detailed Analysis": {
    "Content Discrepancies": {
      "Summary": "...",
      "Findings": [
        {
          "Section": "...",
          "Issue": "...",
          "Details": "...",
          "Code": "...",
          "Recommended Fix": "..."
        }
      ]
    },
    "Styling Discrepancies": {
      "Summary": "...",
      "Findings": [
        {
          "Section": "...",
          "Issue": "...",
          "Details": "...",
          "Code": "...",
          "Recommended Fix": "..."
        }
      ]
    },
    "Intentional Flaws And Known Issues": {
      "Summary": "...",
      "Findings": [
        {
          "Category": "...",
          "Issue": "...",
          "Details": "...",
          "Recommended Fix": "..."
        }
      ]
    },
    "Functional Discrepancies": {
      "Summary": "...",
      "Findings": [
        {
          "Issue": "...",
          "Details": "...",
          "Code": "...",
          "Recommended Fix": "..."
        }
      ]
    }
  },
  "Non-LLM Evaluations": {
    "Accessibility Report": {
      "Summary": "...",
      "Key Findings": [
        {
          "Issue": "...",
          "Recommended Fix": "..."
        }
      ]
    },
    "Performance Report": {
      "Summary": "...",
      "Key Findings": [
        {
          "Issue": "...",
          "Recommended Fix": "..."
        }
      ]
    },
    "Validation Report": {
      "Summary": "...",
      "Key Findings": [
        {
          "Issue": "...",
          "Recommended Fix": "..."
        }
      ]
    },
    "Layout Report": {
      "Summary": "...",
      "Recommended Fix": "..."
    }
  },
  "Other Issues": [
      {
          "Issue": "...",
          "Details": "...",
          "Code": "...",
          "Recommended Fix": "..."
      }
    ]
}
'''
        "\n**Inputs for Analysis:**\n\n"
        f"1. **HTML (Text):**\n{htmlText}\n\n"
        f"2. **Specifications:**\n{specification or 'None'}\n\n"
        f"{'3. Find the Design File attached.\n\n' if designFile else ''}"
        f"**Non-LLM Evaluations:** {"null" if evaluations else ""}\n\n"
    )
    # print(evaluations, nonLLMEvaluations)
    if evaluations.get("axeCoreResult"):
        prompt += f"* **Accessibility Summary:**\n{json.dumps(evaluations['axeCoreResult'], indent=2)}\n\n"
    if evaluations.get("pageSpeedResult") is not None:
        prompt += f"* **Performance Summary:**\n{json.dumps(evaluations['pageSpeedResult'], indent=2)}\n\n"
    if evaluations.get("nuValidatorResult"):
        prompt += f"* **Validation Summary:**\n{json.dumps(evaluations['nuValidatorResult'], indent=2)}\n\n"
    if evaluations.get("responsivenessResult") is not None:
        prompt += f"* **Overflow Status:**\n{json.dumps(evaluations['responsivenessResult'], indent=2)}\n\n"

    return prompt

    
@app.post("/webpage-analysis", response_model=WebpageAnalysisResponse)
async def webpage_analysis(
    htmlText: Annotated[str, Form()],
    specification: Annotated[str | None, Form()] = "",
    webAuditResults: Annotated[str | None, Form()] = "",
    designFile: Annotated[UploadFile | None, File()] = None
):
    """
    Analyzes a webpage using LLM-based evaluation and optional design/audit data.

    Accepts:
        - `htmlText`: The HTML content to be analyzed.
        - `specification`: Optional textual design/functionality guidelines.
        - `webAuditResults`: Optional JSON string containing performance/accessibility/audit data.
        - `designFile`: Optional image file representing the design.

    The endpoint:
        - Validates all inputs and their sizes/types.
        - Parses and verifies the structure of `webAuditResults` if provided.
        - Uploads the `designFile` to Gemini (if given), then deletes it.
        - Constructs a strict prompt for the LLM to respond with JSON only.

    Returns:
        A validated `WebpageAnalysisResponse` Pydantic model based on the LLM output.

    Raises:
        HTTPException:
            - 400: Invalid or missing input data.
            - 500: Unexpected server error during analysis.
    """

    if designFile:
        designFile_content = await designFile.read()
    if not htmlText:
        raise HTTPException(status_code=400, detail="htmlText is required")
    if len(htmlText+specification+webAuditResults)>2*1024*1024:
        raise HTTPException(status_code=400, detail="Files are too large")
    if designFile and len(designFile_content)>5*1024*1024:
        raise HTTPException(status_code=400, detail="Files are too large")
    if designFile and not designFile.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="designFile must be an image")
    if webAuditResults:
        try:
            parsed_audit = json.loads(webAuditResults)
            # Check required keys inside parsed_audit
            required_keys = {"axeCoreResult", "pageSpeedResult", "nuValidatorResult", "responsivenessResult"}
            if not all(key in parsed_audit for key in required_keys):
                raise HTTPException(status_code=400, detail="Invalid webAuditResults structure")
        except (json.JSONDecodeError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid webAuditResults JSON")
    contents = [get_prompt(htmlText=htmlText, specification=specification, designFile=designFile!=None, webAuditResults=webAuditResults)]
    if designFile:
      temp_file_path = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + designFile.filename 
    try:
      if designFile:
          with open(temp_file_path, "wb") as f:
              f.write(designFile_content)
          
          uploaded = client.files.upload(file=temp_file_path)
          contents.append(uploaded)
          os.remove(temp_file_path)
      # contents = [text_prompt, uploaded]
      response = client.models.generate_content(
          model=model,
          contents=contents
      )

      if designFile:
          client.files.delete(name=uploaded.name)
      return_object = json.loads(response.text)
      validated_response = WebpageAnalysisResponse.model_validate(return_object)

      return validated_response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e) or "Error with server")
    finally:
        if designFile and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    