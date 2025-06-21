#mistakes: sending client.post here as files= instead of data=, using pydantic model on endpoint to sending file doesn't work. pydantic is just for json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from .main import app
import os
import app.main as main_module
import pytest
client = TestClient(app)

html_json = {"htmlText": "<h1>Hello</h1>"}
html_spec_json = {"htmlText": "<h1>Hello</h1>", "specification": "Must follow accessibility"}


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_only_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = "Mock: HTML only analysis."
    # JSON content passed as a field in multipart/form-data
    response = client.post(
        "/webpage-analysis",
        data=html_json
    )

    assert response.status_code == 200
    assert response.text == "Mock: HTML only analysis."
    mock_generate.assert_called_once()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_with_specification_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = "Mock: HTML with spec."

    response = client.post(
        "/webpage-analysis",
        data=html_spec_json
    )

    assert response.status_code == 200
    assert "Mock: HTML with spec." in response.text
    mock_generate.assert_called_once()
    mock_delete.assert_not_called()
    mock_upload.assert_not_called()

@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_with_designFile_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = "Mock: HTML with file"
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
    assert "Mock: HTML with file" in response.text
    mock_generate.assert_called_once()
    mock_delete.assert_called_once()
    mock_upload.assert_called_once()

@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_htmlText_with_specification_and_designFile_returns_200(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = "Mock: HTML with file"
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
    assert "Mock: HTML with file" in response.text
    mock_generate.assert_called_once()
    mock_delete.assert_called_once()
    mock_upload.assert_called_once()


@patch("app.main.client.models.generate_content")
@patch("app.main.client.files.upload")
@patch("app.main.client.files.delete")
def test_no_htmlText_throws_error(mock_delete, mock_upload, mock_generate):
    mock_generate.return_value.text = "Mock: HTML only analysis."
    # JSON content passed as a field in multipart/form-data
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
    mock_generate.return_value.text = "Mock: HTML with file"
    mock_upload.return_value.name = "test1.pdf"

    with open("test.pdf", "wb") as f:  # dummy image
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
    mock_generate.return_value.text = "Mock: HTML only analysis."
    # JSON content passed as a field in multipart/form-data
    response = client.post(
        "/webpage-analysis",
        data={"htmlText": "<h1>HELLO WORLD</h1>"*3000}
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
    mock_generate.return_value.text = "Mock: HTML only analysis."
    # JSON content passed as a field in multipart/form-data
    response = client.post(
        "/webpage-analysis",
        data={"htmlText": "<h1>HELLO WORLD</h1>", "specification": "This is a html file"*5000}
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
    mock_generate.return_value.text = "Mock: HTML with file"
    mock_upload.return_value.name = "test1.pdf"

    main_module.client.files.upload = mock_upload

    with open("test.png", "wb") as f:  # dummy image
        f.write(b"\x89PNG\r\n\x1a\n"*700000)

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
