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
from .models import WebpageAnalysisResponse
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
model = os.getenv("MODEL")
app = FastAPI()

# Load Gemini client
client = get_client()

class AnalysisRequest(BaseModel):
    htmlText: Annotated[str | None, Form()] = None
    specification: Annotated[str | None, Form()] = None
    designFile: Annotated[UploadFile | None, File()] = None
@app.get("/", response_class=HTMLResponse)
async def root():
    # print(os.getenv("GEMINI_API_KEY"))
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Webpage Analysis Form</title>
  <style>
    #responseBox {
      margin-top: 20px;
      padding: 10px;
      border: 1px solid #ccc;
      background-color: #f7f7f7;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <h2>Submit Webpage for Analysis</h2>
  <form id="analysisForm">
    <label for="htmlText">HTML Text:</label><br>
    <textarea id="htmlText" name="htmlText" rows="5" cols="50"></textarea><br><br>

    <label for="specification">Specification:</label><br>
    <textarea type="text" id="specification" name="specification" rows="5" cols="50"></textarea><br><br>

    <label for="designFile">Design File:</label><br>
    <input type="file" id="designFile" name="designFile"><br><br>

    <button type="submit">Submit</button>
  </form>

  <div id="responseBox">Response will appear here...</div>

  <script>
    const form = document.getElementById("analysisForm");
    const responseBox = document.getElementById("responseBox");

    form.addEventListener("submit", async function (event) {
  event.preventDefault();

  const formData = new FormData();

  const htmlText = document.getElementById("htmlText").value;
  const specification = document.getElementById("specification").value;
  const designFileInput = document.getElementById("designFile");

  if (htmlText.trim()) {
    formData.append("htmlText", htmlText);
  }

  if (specification.trim()) {
    formData.append("specification", specification);
  }

  if (designFileInput.files.length > 0) {
    formData.append("designFile", designFileInput.files[0]);
  }
  responseBox.textContent = "LOADING...";
  try {const response = await fetch("http://localhost:8000/webpage-analysis", {
    method: "POST",
    body: formData
  });

  const text = await response.text();
  responseBox.textContent = text;
  }
  catch(e){
    responseBox.textContent = e.message;
  }finally{

  }
});

  </script>
</body>
</html>


    """

def get_prompt(htmlText: str, specification: str | None = "", designFile: bool = False, webAuditResults: str = "") -> str:

    try:
        evaluations = json.loads(webAuditResults) if webAuditResults else {}
    except json.JSONDecodeError:
        evaluations = {}

    prompt = (
        "Please perform a comprehensive UI analysis of the html mentioned and generate strictly a JSON report "
        "(No additional text except the JSON response: Start with \"{\", end with \"}\". No markdown. Raw JSON as text.). The output must strictly follow the JSON structure provided "
        "in the 'Example Output Format' section below. Fill in the data based on my inputs, ensuring no deviation "
        "from the provided keys, nesting, or data types. Fill key \"code\" with the affected html code only. Fill the key \"Non-LLM Evaluations\" as null if input non-LLM Evaluations are not given (\"Non-LLM Evaluations\": null). Fill any key in inapplicable, fill it as null.\n\n"
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
    # print(get_prompt(htmlText, specification, designFile!=None, webAuditResults))
    # obj = {
    #   "Executive Summary": "This is a summary of the LLM analysis.",
    #   "Detailed Analysis": {
    #     "Content Discrepancies": {
    #       "Summary": "Content issues found.",
    #       "Findings": [
    #         {
    #           "Section": "Header",
    #           "Issue": "Incorrect tag usage",
    #           "Details": "Used <span> instead of <h1>.",
    #           "Code": "<span>Title</span>",
    #           "Recommended Fix": "Replace <span> with <h1>."
    #         }
    #       ]
    #     },
    #     "Styling Discrepancies": {
    #       "Summary": "Styling issues found.",
    #       "Findings": [
    #         {
    #           "Section": "Button",
    #           "Issue": "Low contrast text",
    #           "Details": "Text color fails WCAG contrast ratio.",
    #           "Code": ".btn { color: #999; }",
    #           "Recommended Fix": "Use darker text color."
    #         }
    #       ]
    #     },
    #     "Intentional Flaws And Known Issues": {
    #       "Summary": "Known intentional issues.",
    #       "Findings": [
    #         {
    #           "Category": "HTML Validation",
    #           "Issue": "Invalid attribute used",
    #           "Details": "Custom attribute not allowed by spec.",
    #           "Recommended Fix": "Remove or replace with data-* attribute."
    #         }
    #       ]
    #     },
    #     "Functional Discrepancies": {
    #       "Summary": "No functional discrepancies detected.",
    #       "Findings": []
    #     }
    #   },
    #   "Non-LLM Evaluations": {
    #     "Accessibility Report": {
    #       "Summary": "Accessibility check summary.",
    #       "Key Findings": [
    #         {
    #           "Issue": "Missing alt text on images",
    #           "Recommended Fix": "Add alt attributes."
    #         }
    #       ]
    #     },
    #     "Performance Report": {
    #       "Summary": "Performance metrics summary.",
    #       "Key Findings": [
    #         {
    #           "Issue": "Large image sizes",
    #           "Recommended Fix": "Optimize image assets."
    #         }
    #       ]
    #     },
    #     "Validation Report": {
    #       "Summary": "Validation results summary.",
    #       "Key Findings": [
    #         {
    #           "Issue": "Unclosed HTML tags",
    #           "Recommended Fix": "Ensure all tags are properly closed."
    #         }
    #       ]
    #     },
    #     "Layout Report": {
    #       "Summary": "Layout check summary.",
    #       "Recommended Fix": "Fix overlapping elements on mobile view."
    #     }
    #   },
    #   "Other Issues": [
    #     {
    #       "Issue": "Deprecated HTML tag used",
    #       "Details": "The <center> tag is obsolete.",
    #       "Code": "<center>Content</center>",
    #       "Recommended Fix": "Use CSS for centering."
    #     }
    #   ]
    # }
    # return JSONResponse(content=obj)
    # return "HELLO IT WORKS"
    # return JSONResponse({'Mock': 'HTML only analysis.'})
    if designFile:
        designFile_content = await designFile.read()
    if not htmlText:
        raise HTTPException(status_code=400, detail="htmlText is required")
    if len(htmlText+specification+webAuditResults)>2000000:
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
    try:
      if designFile:
          temp_file_path = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + designFile.filename 

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
        raise HTTPException(status_code=500, detail=str(e) or "Error with server")
    