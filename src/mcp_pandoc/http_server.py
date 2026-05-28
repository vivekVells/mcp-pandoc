"""HTTP server for mcp-pandoc with Streamable HTTP transport."""
import os
import time

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response

from . import server
from .file_registry import registry

AUTH_TOKEN = os.environ.get("MCP_PANDOC_AUTH_TOKEN", "")
PORT = int(os.environ.get("MCP_PANDOC_PORT", "8080"))
BASE_URL = os.environ.get("MCP_PANDOC_BASE_URL", f"http://localhost:{PORT}")


class SimpleTokenVerifier(TokenVerifier):
    """Verifies bearer tokens against a single static token."""

    async def verify_token(self, token: str) -> AccessToken | None:
        if not AUTH_TOKEN:
            return None
        if token != AUTH_TOKEN:
            return None
        return AccessToken(
            token=token,
            client_id="mcp-pandoc",
            scopes=["mcp:tools", "mcp:upload", "mcp:download"],
        )


def _check_auth(request: Request) -> bool:
    """Check Bearer token from Authorization header."""
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth[7:]
    return bool(AUTH_TOKEN) and token == AUTH_TOKEN


def configure_app() -> None:
    """Configure the shared FastMCP instance with auth and routes."""
    server.server.settings.host = "0.0.0.0"
    server.server.settings.port = PORT
    server.server.settings.stateless_http = True

    if AUTH_TOKEN:
        server.server._token_verifier = SimpleTokenVerifier()
        server.server.settings.auth = AuthSettings(
            issuer_url=BASE_URL,
            resource_server_url=BASE_URL,
        )

    @server.server.custom_route("/upload/{file_id}", methods=["POST"])
    async def handle_upload(request: Request) -> Response:
        file_id = request.path_params.get("file_id")
        if not file_id:
            return JSONResponse({"error": "missing file_id in path"}, status_code=400)

        try:
            form = await request.form()
            file = form.get("file")
            if file is None:
                return JSONResponse({"error": "missing file field"}, status_code=400)

            if hasattr(file, "read"):
                file_bytes = await file.read()
                filename = getattr(file, "filename", "upload") or "upload"
            else:
                return JSONResponse({"error": "invalid file field"}, status_code=400)

            ok = await registry.complete_session(file_id, file_bytes, filename)
            if not ok:
                return JSONResponse({"error": "invalid or expired file_id"}, status_code=404)

            return JSONResponse({"file_id": file_id, "uploaded_at": time.time()})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @server.server.custom_route("/download/{file_id}", methods=["GET"])
    async def handle_download(request: Request) -> Response:
        file_id = request.path_params.get("file_id")
        if not file_id:
            return JSONResponse({"error": "missing file_id"}, status_code=400)

        info = registry.get_info(file_id)
        if not info:
            return JSONResponse({"error": "file not found"}, status_code=404)

        return FileResponse(
            path=info["path"],
            filename=info["filename"],
            media_type="application/octet-stream",
        )


async def run_http():
    """Run the HTTP server."""
    await registry.initialize()
    configure_app()
    await server.server.run_streamable_http_async()
