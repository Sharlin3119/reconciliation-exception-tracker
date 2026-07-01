import io

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_upload_marks_allowed_flags(client):
    files = [
        ("files", ("report.pdf", io.BytesIO(b"x"), "application/pdf")),
        ("files", ("sheet.XLSX", io.BytesIO(b"x"), "application/octet-stream")),
        ("files", ("notes.txt", io.BytesIO(b"x"), "text/plain")),
    ]
    res = client.post("/files/upload", files=files)
    assert res.status_code == 200

    data = res.json()
    assert "files" in data
    assert len(data["files"]) == 3

    by_name = {f["filename"]: f["allowed"] for f in data["files"]}
    assert by_name["report.pdf"] is True
    assert by_name["sheet.XLSX"] is True  # case-insensitive extension
    assert by_name["notes.txt"] is False
