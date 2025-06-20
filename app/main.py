from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, Annotated
import os
import google.genai as genai
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
app = FastAPI()

# Load Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class AnalysisRequest(BaseModel):
    htmlText: Annotated[str | None, Form()] = None
    specification: Annotated[str | None, Form()] = None
    designFile: Annotated[UploadFile | None, File()] = None
@app.get("/", response_class=HTMLResponse)
async def root():
    print(os.getenv("GEMINI_API_KEY"))
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
    <input type="text" id="specification" name="specification"><br><br>

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

      const formData = new FormData(form);

      const response = await fetch("http://localhost:8000/webpage-analysis", {
        method: "POST",
        body: formData
      });

      const text = await response.text();
      responseBox.textContent = text;
    });
  </script>
</body>
</html>


    """
@app.post("/webpage-analysis", response_class=PlainTextResponse)
async def webpage_analysis(
    htmlText: Annotated[str, Form()],
    specification: Annotated[str | None, Form()] = None,
    designFile: Annotated[UploadFile | None, File()] = None
):
    if designFile:
        print(designFile)
    if not htmlText:
        raise HTTPException(status_code=400, detail="htmlText is required")
    if len(htmlText)>50000 or specification and len(specification)>50000:
        raise HTTPException(status_code=400, detail="Files are too large")
    if designFile and len(await designFile.read())>5*1024*1024:
        raise HTTPException(status_code=400, detail="Files are too large")
    contents = []

    if designFile:
        if not designFile.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="designFile must be an image")
        
        with open(designFile.filename, "wb") as f:
            f.write(await designFile.read())

        uploaded = client.files.upload(file=designFile.filename)
        contents.append(uploaded)
        os.remove(designFile.filename)

    text_prompt = f"Analyze the following HTML for UI/UX flaws:\n\nHTML:\n{htmlText}"
    if specification:
        text_prompt += f"\n\nSpecification:\n{specification}"

    contents.append(text_prompt)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )

    if designFile:
        client.files.delete(name=uploaded.name)

    return response.text
