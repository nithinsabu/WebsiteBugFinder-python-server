#mistakes: sending client.post here as files= instead of data=, using pydantic model on endpoint to sending file doesn't work. pydantic is just for json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app
import os
import pytest
import app.main as main
import json
client = TestClient(app)

html_json = {"htmlText": "<h1>Hello</h1>"}
html_spec_json = {"htmlText": "<h1>Hello</h1>", "specification": "Must follow accessibility"}
mock_api_response = {
    "Executive Summary": "Mock summary.",
    "Detailed Analysis": {
        "Content Discrepancies": {
            "Summary": "Mock content summary.",
            "Findings": [
                {
                    "Section": "Mock Section",
                    "Issue": "Mock Issue",
                    "Details": "Mock Details",
                    "Code": "<mock></mock>",
                    "Recommended Fix": "Mock fix."
                }
            ]
        },
        "Styling Discrepancies": {
            "Summary": "Mock styling summary.",
            "Findings": [
                {
                    "Section": "Mock Section",
                    "Issue": "Mock Issue",
                    "Details": "Mock Details",
                    "Code": "<mock></mock>",
                    "Recommended Fix": "Mock fix."
                }
            ]
        },
        "Intentional Flaws And Known Issues": {
            "Summary": "Mock intentional flaws summary.",
            "Findings": [
                {
                    "Category": "Mock Category",
                    "Issue": "Mock Issue",
                    "Details": "Mock Details",
                    "Recommended Fix": "Mock fix."
                }
            ]
        },
        "Functional Discrepancies": {
            "Summary": "Mock functional summary.",
            "Findings": [
                {
                    "Issue": "Mock Issue",
                    "Details": "Mock Details",
                    "Code": "<mock></mock>",
                    "Recommended Fix": "Mock fix."
                }
            ]
        }
    },
    "Non-LLM Evaluations": {
        "Accessibility Report": {
            "Summary": "Mock accessibility summary.",
            "Key Findings": [
                {
                    "Issue": "Mock Issue",
                    "Recommended Fix": "Mock fix."
                }
            ]
        },
        "Performance Report": {
            "Summary": "Mock performance summary.",
            "Key Findings": [
                {
                    "Issue": "Mock Issue",
                    "Recommended Fix": "Mock fix."
                }
            ]
        },
        "Validation Report": {
            "Summary": "Mock validation summary.",
            "Key Findings": [
                {
                    "Issue": "Mock Issue",
                    "Recommended Fix": "Mock fix."
                }
            ]
        },
        "Layout Report": {
            "Summary": "Mock layout summary.",
            "Recommended Fix": "Mock fix."
        }
    },
    "Other Issues": [
        {
            "Issue": "Mock Issue",
            "Details": "Mock Details",
            "Code": "<mock></mock>",
            "Recommended Fix": "Mock fix."
        }
    ]
}

@pytest.fixture(autouse=True)
def mock_gemini_client(monkeypatch):
    mock = Mock()
    mock.models.generate_content = Mock()
    mock.models.generate_content.return_value.text = json.dumps(mock_api_response)
    mock.files.upload = Mock(return_value="mock_upload")
    mock.files.delete = Mock(return_value="mock_delete")
    monkeypatch.setattr(main, "client", mock)
    monkeypatch.setattr(os, "getenv", "mock_api_key")
    from .main import client as imported_client
    assert imported_client.models.generate_content(model="xxx", contents=["xxx"]).text == json.dumps(mock_api_response)

@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_only_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    # JSON content passed as a field in multipart/form-data
    response = client.post(
        "/webpage-analysis",
        data=html_json
    )

    assert response.status_code == 200
    assert json.loads(response.text) == mock_api_response
    mock_generate.assert_called_once()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_with_specification_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    response = client.post(
        "/webpage-analysis",
        data=html_spec_json
    )

    assert response.status_code == 200
    assert json.loads(response.text) == mock_api_response
    mock_generate.assert_called_once()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_with_designFile_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    mock_upload.return_value.name = "test1.png"

    with open("test.png", "wb") as f:  # dummy image
        f.write(b"\x89PNG\r\n\x1a\n")

    with open("test.png", "rb") as file:
        response = client.post(
            "/webpage-analysis",
            data=html_json,
            files={"designFile": (mock_upload.return_value.name, file, "image/png")}
        )

    os.remove("test.png")
    assert response.status_code == 200
    assert json.loads(response.text) == mock_api_response
    mock_generate.assert_called_once()
    mock_delete.assert_called_once()
    mock_upload.assert_called_once()

@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_with_specification_and_designFile_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    mock_upload.return_value.name = "test1.png"

    with open("test.png", "wb") as f:  # dummy image
        f.write(b"\x89PNG\r\n\x1a\n")

    with open("test.png", "rb") as file:
        response = client.post(
            "/webpage-analysis",
            data=html_spec_json,
            files={"designFile": (mock_upload.return_value.name, file, "image/png")}
        )
    os.remove("test.png")
    assert response.status_code == 200
    assert json.loads(response.text) == mock_api_response
    mock_generate.assert_called_once()
    mock_delete.assert_called_once()
    mock_upload.assert_called_once()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_no_htmlText_throws_error(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    response = client.post(
        "/webpage-analysis",
        data={}
    )

    assert response.status_code == 422
    mock_generate.assert_not_called()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()

@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_with_wrong_designFile_format_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    mock_upload.return_value.name = "test1.pdf"

    with open("test.pdf", "wb") as f:  # dummy file
        f.write(b"\x89PNG\r\n\x1a\n")

    with open("test.pdf", "rb") as file:
        response = client.post(
            "/webpage-analysis",
            data=html_spec_json,
            files={"designFile": (mock_upload.return_value.name, file, "application/pdf")}
        )
    os.remove("test.pdf")
    assert response.status_code == 400
    assert "designFile must be an image" in response.text
    mock_generate.assert_not_called()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_large_htmlText_throws_error(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    response = client.post(
        "/webpage-analysis",
        data={"htmlText": "<h1>HELLO WORLD</h1>" * 1000000}
    )

    assert response.status_code == 400
    assert "Files are too large" in response.text
    mock_generate.assert_not_called()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_large_specification_throws_error(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    response = client.post(
        "/webpage-analysis",
        data={"htmlText": "<h1>HELLO WORLD</h1>", "specification": "This is a html file" * 1000000}
    )

    assert response.status_code == 400
    assert "Files are too large" in response.text
    mock_generate.assert_not_called()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_large_designFile_throws_error(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    mock_upload.return_value.name = "test1.png"

    with open("test.png", "wb") as f:  # large dummy image
        f.write(b"\x89PNG\r\n\x1a\n" * 700000)

    with open("test.png", "rb") as file:
        response = client.post(
            "/webpage-analysis",
            data=html_json,
            files={"designFile": (mock_upload.return_value.name, file, "image/png")}
        )
    os.remove("test.png")
    assert response.status_code == 400
    assert "Files are too large" in response.text
    mock_generate.assert_not_called()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()

@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_webAuditResults_invalid_json_throws_400(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    response = client.post(
        "/webpage-analysis",
        data={
            "htmlText": "<h1>Test</h1>",
            "webAuditResults": "{invalid json}"
        }
    )

    assert response.status_code == 400
    assert "Invalid webAuditResults JSON" in response.text
    mock_generate.assert_not_called()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_webAuditResults_missing_keys_throws_400(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = json.dumps(mock_api_response)
    response = client.post(
        "/webpage-analysis",
        data={
            "htmlText": "<h1>Test</h1>",
            "webAuditResults": json.dumps({"axeCoreResult": []})  # missing other keys
        }
    )

    assert response.status_code == 400
    assert "Invalid webAuditResults structure" in response.text
    mock_generate.assert_not_called()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()

