from __future__ import annotations

import hashlib
import hmac
import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from orchestration.config import ListenerConfig
from orchestration.reporting import report_result
from orchestration.router import Router

LOGGER = logging.getLogger("github_webhook_listener")
SUPPORTED_EVENTS = {"issues", "issue_comment"}
SUPPORTED_ISSUE_ACTIONS = {"opened", "edited", "labeled", "unlabeled", "reopened"}
SUPPORTED_COMMENT_ACTIONS = {"created"}


class WebhookHandler(BaseHTTPRequestHandler):
    server_version = "GitHubWebhookListener/0.1"

    def _json_response(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/github/webhook":
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        delivery_id = self.headers.get("X-GitHub-Delivery", "")
        event_type = self.headers.get("X-GitHub-Event", "")
        signature = self.headers.get("X-Hub-Signature-256", "")
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        if not self.server.config.github_webhook_secret:
            LOGGER.error("Missing GITHUB_WEBHOOK_SECRET; refusing webhook delivery_id=%s", delivery_id)
            self._json_response(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "missing_secret"})
            return

        if not _verify_signature(raw_body, signature, self.server.config.github_webhook_secret):
            LOGGER.warning("Signature verification failed delivery_id=%s event=%s", delivery_id, event_type)
            self._json_response(HTTPStatus.UNAUTHORIZED, {"error": "invalid_signature"})
            return

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            LOGGER.warning("Malformed payload delivery_id=%s event=%s", delivery_id, event_type)
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "invalid_payload"})
            return

        normalized_event = _normalize_event(payload, event_type, delivery_id)
        if normalized_event is None:
            LOGGER.info("Ignoring unsupported event delivery_id=%s event=%s", delivery_id, event_type)
            self._json_response(HTTPStatus.OK, {"status": "ignored", "reason": "unsupported_event"})
            return

        repo_name = normalized_event["repository_full_name"]
        action = normalized_event["action"]

        if repo_name not in self.server.config.allowed_repos:
            LOGGER.info("Ignoring repo not in allowlist delivery_id=%s repo=%s", delivery_id, repo_name)
            self._json_response(HTTPStatus.OK, {"status": "ignored", "reason": "repo_not_allowed"})
            return

        if not _is_actionable(normalized_event):
            LOGGER.info(
                "Ignoring non-actionable event delivery_id=%s repo=%s event=%s action=%s",
                delivery_id,
                repo_name,
                event_type,
                action,
            )
            self._json_response(HTTPStatus.OK, {"status": "ignored", "reason": "not_actionable"})
            return

        LOGGER.info(
            "Accepted event delivery_id=%s repo=%s event=%s action=%s issue=%s",
            delivery_id,
            repo_name,
            event_type,
            action,
            normalized_event.get("issue_number"),
        )
        router_result = self.server.router.handle_event(normalized_event)
        runner_result = router_result.get("runner_result")
        reporting_result = None
        if router_result.get("accepted") and runner_result:
            reporting_result = report_result(repo_name, normalized_event["issue_number"], runner_result)
        self._json_response(
            HTTPStatus.ACCEPTED,
            {"status": "accepted", "router": router_result, "reporting": reporting_result},
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        LOGGER.debug("HTTP %s", format % args)


class WebhookServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], config: ListenerConfig, router: Router):
        super().__init__(server_address, WebhookHandler)
        self.config = config
        self.router = router


def _verify_signature(raw_body: bytes, received_signature: str, secret: str) -> bool:
    if not received_signature.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", received_signature)


def _normalize_event(payload: dict[str, Any], event_type: str, delivery_id: str) -> dict[str, Any] | None:
    if event_type not in SUPPORTED_EVENTS:
        return None

    issue = payload.get("issue") or {}
    repository = payload.get("repository") or {}
    labels = [label.get("name") for label in issue.get("labels", []) if label.get("name")]
    comment = payload.get("comment") or {}
    sender = payload.get("sender") or {}

    return {
        "delivery_id": delivery_id,
        "event_type": event_type,
        "action": payload.get("action", ""),
        "repository_full_name": repository.get("full_name", ""),
        "issue_number": issue.get("number"),
        "issue_title": issue.get("title", ""),
        "issue_body": issue.get("body", ""),
        "issue_state": issue.get("state", ""),
        "labels": labels,
        "comment_body": comment.get("body", ""),
        "sender_login": sender.get("login", ""),
        "html_url": issue.get("html_url", ""),
        "received_at": payload.get("repository", {}).get("updated_at"),
    }


def _is_actionable(normalized_event: dict[str, Any]) -> bool:
    event_type = normalized_event["event_type"]
    action = normalized_event["action"]
    issue_state = normalized_event["issue_state"]

    if event_type == "issues":
        return issue_state == "open" and action in SUPPORTED_ISSUE_ACTIONS

    if event_type == "issue_comment":
        if action not in SUPPORTED_COMMENT_ACTIONS:
            return False
        body = (normalized_event.get("comment_body") or "").strip()
        return body.startswith("/retry") or body.startswith("/status") or body.startswith("/hold")

    return False


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    config = ListenerConfig.from_env()
    router = Router()
    server = WebhookServer((config.host, config.port), config, router)
    LOGGER.info(
        "Starting GitHub webhook listener host=%s port=%s allowed_repos=%s",
        config.host,
        config.port,
        ",".join(config.allowed_repos),
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
