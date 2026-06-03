"""File registry with persistent manifest for uploads and outputs."""
import asyncio
import json
import os
import time
import uuid
from typing import Optional

UPLOAD_DIR = os.environ.get("MCP_PANDOC_UPLOAD_DIR", "/tmp/uploads")
TTL_DAYS = int(os.environ.get("MCP_PANDOC_UPLOAD_TTL_DAYS", "7"))
MAX_SIZE_MB = int(os.environ.get("MCP_PANDOC_UPLOAD_MAX_SIZE_MB", "2048"))
GC_INTERVAL_SECONDS = int(os.environ.get("MCP_PANDOC_GC_INTERVAL_SECONDS", "60"))
MANIFEST_FILE = "files.json"


class FileRegistry:
    """Manages opaque file ID to real path mapping with persistent manifest."""

    _instance: Optional["FileRegistry"] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._mapping: dict[str, dict] = {}
        self._last_gc_time: float = 0
        self._initialized = True

    async def initialize(self):
        """Load existing manifest from disk."""
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        manifest_path = os.path.join(UPLOAD_DIR, MANIFEST_FILE)
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                for file_id, info in data.items():
                    real_path = info.get("path")
                    if real_path and os.path.exists(real_path):
                        self._mapping[file_id] = info
                    else:
                        print(f"[file_registry] stale entry removed: {file_id} -> {real_path}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[file_registry] failed to load manifest: {e}")
        print(f"[file_registry] initialized with {len(self._mapping)} entries from {UPLOAD_DIR}")

    async def create_session(self, filename: str = "upload") -> str:
        """Generate a FILE-ID for an upload session before the file is uploaded."""
        async with self._lock:
            file_id = uuid.uuid4().hex
            self._mapping[file_id] = {
                "path": None,
                "filename": filename,
                "size": 0,
                "created_at": time.time(),
                "type": "pending",
            }
            await self._save_manifest()
            return file_id

    async def complete_session(self, file_id: str, file_bytes: bytes, filename: str) -> bool:
        """Save file bytes to a pending session."""
        async with self._lock:
            info = self._mapping.get(file_id)
            if not info or info.get("type") != "pending":
                return False
            ext = os.path.splitext(filename)[1] or os.path.splitext(info.get("filename", ""))[1] or ""
            real_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
            with open(real_path, "wb") as f:
                f.write(file_bytes)
            info["path"] = real_path
            info["filename"] = filename
            info["size"] = len(file_bytes)
            info["type"] = "upload"
            await self._save_manifest()
            return True

    async def register(self, file_bytes: bytes, filename: str) -> str:
        """Save uploaded file and return opaque ID."""
        async with self._lock:
            file_id = uuid.uuid4().hex
            ext = os.path.splitext(filename)[1] or ""
            real_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
            with open(real_path, "wb") as f:
                f.write(file_bytes)
            self._mapping[file_id] = {
                "path": real_path,
                "filename": filename,
                "size": len(file_bytes),
                "created_at": time.time(),
                "type": "upload",
            }
            await self._save_manifest()
            return file_id

    def register_output(self, real_path: str, filename: str) -> str:
        """Register an output file and return opaque ID."""
        file_id = uuid.uuid4().hex
        size = os.path.getsize(real_path) if os.path.exists(real_path) else 0
        self._mapping[file_id] = {
            "path": real_path,
            "filename": filename,
            "size": size,
            "created_at": time.time(),
            "type": "output",
        }
        self._save_manifest_sync()
        return file_id

    def resolve(self, file_id: str) -> str | None:
        """Resolve opaque ID to real filesystem path."""
        info = self._mapping.get(file_id)
        if info and os.path.exists(info["path"]):
            return info["path"]
        if info and not os.path.exists(info["path"]):
            del self._mapping[file_id]
        return None

    def get_info(self, file_id: str) -> dict | None:
        """Get file metadata by opaque ID."""
        info = self._mapping.get(file_id)
        if info and os.path.exists(info["path"]):
            return info
        if info:
            del self._mapping[file_id]
        return None

    async def gc(self) -> dict:
        """Run garbage collection with age and size policies."""
        if not self._should_run_gc():
            return {"skipped": True, "reason": "gc_paced"}

        async with self._lock:
            deleted = []
            now = time.time()
            ttl_seconds = TTL_DAYS * 86400

            for file_id, info in list(self._mapping.items()):
                if now - info["created_at"] > ttl_seconds:
                    try:
                        os.remove(info["path"])
                    except OSError:
                        pass
                    deleted.append(file_id)

            for file_id in deleted:
                del self._mapping[file_id]

            evicted = await self._evict_by_size()
            deleted.extend(evicted)

            self._last_gc_time = now
            await self._save_manifest()

            return {
                "skipped": False,
                "deleted_count": len(deleted),
                "deleted_ids": deleted,
            }

    def _should_run_gc(self) -> bool:
        return (time.time() - self._last_gc_time) >= GC_INTERVAL_SECONDS

    async def _evict_by_size(self) -> list[str]:
        """Delete oldest files until dir is under MAX_SIZE_MB."""
        max_bytes = MAX_SIZE_MB * 1024 * 1024
        current_size = sum(info["size"] for info in self._mapping.values())

        if current_size <= max_bytes:
            return []

        sorted_entries = sorted(self._mapping.items(), key=lambda x: x[1]["created_at"])
        evicted = []

        for file_id, info in sorted_entries:
            if current_size <= max_bytes:
                break
            try:
                os.remove(info["path"])
            except OSError:
                pass
            current_size -= info["size"]
            evicted.append(file_id)

        for file_id in evicted:
            del self._mapping[file_id]

        return evicted

    async def _save_manifest(self):
        """Persist mapping to disk."""
        manifest_path = os.path.join(UPLOAD_DIR, MANIFEST_FILE)
        try:
            with open(manifest_path, "w") as f:
                json.dump(self._mapping, f, indent=2)
        except OSError as e:
            print(f"[file_registry] failed to save manifest: {e}")

    def _save_manifest_sync(self):
        """Persist mapping to disk (synchronous)."""
        manifest_path = os.path.join(UPLOAD_DIR, MANIFEST_FILE)
        try:
            with open(manifest_path, "w") as f:
                json.dump(self._mapping, f, indent=2)
        except OSError as e:
            print(f"[file_registry] failed to save manifest: {e}")


registry = FileRegistry()
