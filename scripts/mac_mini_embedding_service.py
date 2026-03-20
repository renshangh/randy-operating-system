#!/usr/bin/env python3
"""Lightweight local embedding HTTP service for Mac Mini.

Phase 1 for randy-operating-system#191.
Uses sentence-transformers with BAAI/bge-small-en-v1.5 and exposes a
minimal JSON API over localhost by default.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
DEFAULT_HOST = os.environ.get("EMBED_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("EMBED_PORT", "8011"))
DEFAULT_NORMALIZE = os.environ.get("EMBED_NORMALIZE", "1") != "0"

_model: SentenceTransformer | None = None
_model_name: str = DEFAULT_MODEL
_normalize: bool = DEFAULT_NORMALIZE


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_model_name)
    return _model


def embed_texts(inputs: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = model.encode(inputs, normalize_embeddings=_normalize)
    return [list(map(float, row)) for row in vectors]


class Handler(BaseHTTPRequestHandler):
    server_version = "MacMiniEmbeddingService/0.1"

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(
                {
                    "ok": True,
                    "model": _model_name,
                    "normalize": _normalize,
                }
            )
            return
        self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/embed":
            self._send_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            inputs = payload.get("input")
            if isinstance(inputs, str):
                texts = [inputs]
            elif isinstance(inputs, list) and all(isinstance(x, str) for x in inputs):
                texts = inputs
            else:
                self._send_json(
                    {"error": "input must be a string or list of strings"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            vectors = embed_texts(texts)
            self._send_json(
                {
                    "model": _model_name,
                    "dimensions": len(vectors[0]) if vectors else 0,
                    "data": [{"embedding": vec, "index": i} for i, vec in enumerate(vectors)],
                }
            )
        except Exception as exc:  # pragma: no cover
            self._send_json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), fmt % args))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Mac Mini embedding service")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--no-normalize", action="store_true")
    args = parser.parse_args()

    global _model_name, _normalize
    _model_name = args.model
    _normalize = not args.no_normalize

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"embedding service listening on http://{args.host}:{args.port} model={_model_name} normalize={_normalize}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
