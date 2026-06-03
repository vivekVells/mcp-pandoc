"""Integration tests for HTTP transport mode."""
import asyncio
import json
import os
import re
import subprocess
import time

import pytest

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:18080")
AUTH_TOKEN = os.environ.get("MCP_PANDOC_AUTH_TOKEN", "test-token-123")
IS_REMOTE = BASE_URL.startswith("https://")


@pytest.fixture(scope="module", autouse=True)
def start_server():
    """Start the HTTP server locally if not testing against a remote."""
    if IS_REMOTE:
        yield
        return

    env = os.environ.copy()
    env.update({
        "MCP_PANDOC_TRANSPORT": "http",
        "MCP_PANDOC_AUTH_TOKEN": AUTH_TOKEN,
        "MCP_PANDOC_PORT": "18080",
        "MCP_PANDOC_UPLOAD_DIR": "/tmp/mcp-pandoc-test-uploads",
        "MCP_PANDOC_BASE_URL": "http://localhost:18080",
    })
    os.makedirs("/tmp/mcp-pandoc-test-uploads", exist_ok=True)

    proc = subprocess.Popen(
        ["uv", "run", "mcp-pandoc"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(3)
    yield
    proc.terminate()
    proc.wait()


def mcp_call(method, params):
    """Make an MCP call via HTTP."""
    import urllib.request

    url = f"{BASE_URL}/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode()

    data_lines = [line[5:] for line in raw.split("\n") if line.startswith("data: ")]
    data_json = "".join(data_lines)
    return json.loads(data_json)


def http_post(url, file_path):
    """POST a file to an upload URL."""
    import urllib.request

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    filename = os.path.basename(file_path)
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def http_get(url):
    """GET a download URL."""
    import urllib.request

    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


class TestHTTPTransport:
    """Tests for HTTP mode tools and endpoints."""

    def test_tools_list(self):
        """Verify HTTP mode exposes create_upload_session and convert_contents."""
        result = mcp_call("tools/list", {})
        tool_names = [t["name"] for t in result["result"]["tools"]]
        assert "create_upload_session" in tool_names
        assert "convert_contents" in tool_names

    def test_create_upload_session(self):
        """Test create_upload_session returns upload URL and file ID."""
        result = mcp_call("tools/call", {
            "name": "create_upload_session",
            "arguments": {"filename": "test.md"},
        })
        content = json.loads(result["result"]["content"][0]["text"])
        assert "upload_url" in content
        assert "uploaded_file_id" in content
        assert content["upload_url"].endswith(f"/upload/{content['uploaded_file_id']}")

    def test_upload_and_convert(self, tmp_path):
        """Test full upload → convert → download workflow."""
        test_file = tmp_path / "input.md"
        test_file.write_text("# Hello\n\nThis is a test.")

        session = mcp_call("tools/call", {
            "name": "create_upload_session",
            "arguments": {"filename": "input.md"},
        })
        session_data = json.loads(session["result"]["content"][0]["text"])
        file_id = session_data["uploaded_file_id"]
        upload_url = session_data["upload_url"]

        upload_resp = http_post(upload_url, str(test_file))
        assert upload_resp["file_id"] == file_id

        convert = mcp_call("tools/call", {
            "name": "convert_contents",
            "arguments": {
                "uploaded_file_id": file_id,
                "input_format": "markdown",
                "output_format": "html",
                "return_download_url": True,
            },
        })
        convert_text = convert["result"]["content"][0]["text"]
        download_url = re.search(r"Download:\s*(https?://\S+)", convert_text).group(1)

        downloaded = http_get(download_url)
        assert b"<h1" in downloaded or b"<p" in downloaded

    def test_pdf_conversion(self):
        """Test PDF conversion with CJK content."""
        convert = mcp_call("tools/call", {
            "name": "convert_contents",
            "arguments": {
                "contents": "# 测试\n\n这是中文内容。",
                "input_format": "markdown",
                "output_format": "pdf",
                "return_download_url": True,
            },
        })
        convert_text = convert["result"]["content"][0]["text"]
        assert "Download:" in convert_text
        download_url = re.search(r"Download:\s*(https?://\S+)", convert_text).group(1)

        downloaded = http_get(download_url)
        assert len(downloaded) > 0
        assert downloaded.startswith(b"%PDF")

    def test_invalid_file_id_returns_404(self, tmp_path):
        """Test that uploading to an invalid file_id returns 404."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        import urllib.request
        import urllib.error

        url = f"{BASE_URL}/upload/nonexistent-file-id"
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n"
            "test\r\n"
            f"--{boundary}--\r\n"
        ).encode()

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(req, timeout=10)
        assert exc_info.value.code == 404
