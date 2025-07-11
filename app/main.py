from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel
from typing import Annotated
import os
from app.gemini_client import get_client

app = FastAPI()

# Load Gemini client
client = get_client()

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


@app.post("/webpage-analysis", response_class=PlainTextResponse)
async def webpage_analysis(
    htmlText: Annotated[str, Form()],
    specification: Annotated[str | None, Form()] = "",
    designFile: Annotated[UploadFile | None, File()] = None
):
    # return "HELLO IT WORKS"
    if designFile:
        designFile_content = await designFile.read()
    if not htmlText:
        raise HTTPException(status_code=400, detail="htmlText is required")
    if len(htmlText+specification)>1800000:
        raise HTTPException(status_code=400, detail="Files are too large")
    if designFile and len(designFile_content)>2*1024*1024:
        raise HTTPException(status_code=400, detail="Files are too large")
    if designFile and not designFile.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="designFile must be an image")
        
    contents = []
    text_prompt = f"Analyze the following HTML for UI/UX flaws:\n\nHTML:\n{htmlText}"
    if specification:
        text_prompt += f"\n\nSpecification:\n{specification}"
    if designFile:
        text_prompt += "\nUse the design file attached."
    contents.append(text_prompt)

    if designFile:
        temp_file_path = designFile.filename
        with open(temp_file_path, "wb") as f:
            f.write(designFile_content)
        
        uploaded = client.files.upload(file=temp_file_path)
        contents.append(uploaded)
        os.remove(temp_file_path)
    # contents = [text_prompt, uploaded]
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )

    if designFile:
        client.files.delete(name=uploaded.name)
    return response.text

    