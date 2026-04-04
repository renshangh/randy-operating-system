from __future__ import annotations

import hashlib
import hmac
import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from orchestration.config import ListenerConfig
from orchestration.reporting import report_result
from orchestration.router import Router
from orchestration.session_client import SessionClient
from orchestration.task_packet import build_session_event_packet

LOGGER = logging.getLogger("github_webhook_listener")
SUPPORTED_EVENTS = {"issues", "issue_comment"}
SUPPORTED_ISSUE_ACTIONS = {"opened", "edited", "labeled", "reopened"}
SUPPORTED_COMMENT_ACTIONS = {"created"}
DISPATCH_READY_LABEL = "dispatch:ready"
STATUS_DONE_LABEL = "status:done"


class WebhookHandler(BaseHTTPRequestHandler):
    server_version = "GitHubWebhookListener/0.1"

    def _json_response(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self._json_response(200, {"status": "ok"})

    def do_GET(self):
        self._json_response(200, {"status": "ok"})

    def do_HEAD(self):
        self._json_response(200, {"status": "ok"})
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
        LOGGER.info("Router result: %s", router_result)
        runner_result = router_result.get("runner_result")
        reporting_result = None
        delivery_result = None
        discord_result = None
        if router_result.get("accepted") and runner_result:
            reporting_result = report_result(repo_name, normalized_event["issue_number"], runner_result)
        if router_result.get("accepted") and router_result.get("requires_aether_wake"):
            packet = build_session_event_packet(normalized_event, router_result)
            delivery_result = self.server.session_client.send_event(packet)

            if delivery_result.ok:
                self.server.router.ledger.mark_session_send(
                    normalized_event["delivery_id"],
                    "sent",
                    session_label=delivery_result.session_label,
                    session_key=delivery_result.session_id,
                )
                ack_status = "acked" if delivery_result.status in {"acked", "duplicate"} else delivery_result.status
                self.server.router.ledger.mark_ack_status(
                    normalized_event["delivery_id"],
                    ack_status,
                    action=getattr(delivery_result, "action", None),
                    message=None if delivery_result.status == "acked" else delivery_result.status,
                )
            else:
                self.server.router.ledger.mark_session_send(
                    normalized_event["delivery_id"],
                    delivery_result.status,
                    session_label=delivery_result.session_label,
                    session_key=delivery_result.session_id,
                    error=delivery_result.error,
                )
        if router_result.get("accepted"):
            discord_result = _send_discord_heartbeat(self.server.config, normalized_event, router_result, delivery_result)
            if discord_result:
                self.server.router.ledger.mark_discord_notice(
                    normalized_event["delivery_id"],
                    "sent" if discord_result.get("sent") else "failed",
                    error=discord_result.get("error"),
                )
        self._json_response(
            HTTPStatus.ACCEPTED,
            {
                "status": "accepted",
                "router": router_result,
                "reporting": reporting_result,
                "direct_wake": None if delivery_result is None else delivery_result.__dict__,
                "discord": discord_result,
            },
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        LOGGER.debug("HTTP %s", format % args)


class WebhookServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], config: ListenerConfig, router: Router):
        super().__init__(server_address, WebhookHandler)
        self.config = config
        self.router = router
        self.session_client = SessionClient(config)


def _send_discord_heartbeat(
    config: ListenerConfig,
    normalized_event: dict[str, Any],
    router_result: dict[str, Any],
    direct_wake_result: Any | None = None,
) -> dict[str, Any] | None:
    if not (
        router_result.get("status", "").startswith("completion:")
        or router_result.get("status", "").startswith("command:")
    ):
        return {"sent": False, "reason": "not_notice_event"}

    issue_number = normalized_event.get("issue_number")
    repo_name = normalized_event.get("repository_full_name")
    issue_url = normalized_event.get("issue_url") or ""
    status = (router_result.get("status") or "completion:unknown").split(":", 1)[-1]
    agent = (router_result.get("agent") or "unknown").lower()
    summary = router_result.get("summary") or "No summary provided."

    general_webhook = config.discord_general_webhook_url.strip() or config.discord_heartbeat_webhook_url.strip()
    if status == "done":
        webhook_url = general_webhook
    else:
        webhook_map = {
            "mark": config.discord_mark_webhook_url.strip(),
            "social": config.discord_social_webhook_url.strip(),
            "sarah": config.discord_sarah_webhook_url.strip(),
            "ember": config.discord_ember_webhook_url.strip(),
            "sentinel": config.discord_sentinel_webhook_url.strip(),
            "aether": general_webhook,
            "main": general_webhook,
        }
        webhook_url = webhook_map.get(agent) or general_webhook
    if not webhook_url:
        return {"sent": False, "reason": "webhook_not_configured", "agent": agent}

    mention = f"<@{config.discord_aether_user_id}>\n" if (status == "done" or agent in {"aether", "main"}) and config.discord_aether_user_id else ""

    content = (
        f"{mention}Agent return: {agent}\n"
        f"Repo: {repo_name}\n"
        f"Issue: #{issue_number}\n"
        f"State: status:{status}\n"
        f"Summary: {summary}"
    )
    if issue_url:
        content += f"\nURL: {issue_url}"

    payload = json.dumps({"content": content}).encode("utf-8")
    req = request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "openclaw-github-webhook-listener/1.0",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as response:
            status_code = getattr(response, "status", response.getcode())
        LOGGER.info(
            "Discord heartbeat sent repo=%s issue=%s status=%s agent=%s http_status=%s",
            repo_name,
            issue_number,
            status,
            agent,
            status_code,
        )
        return {"sent": True, "http_status": status_code, "agent": agent}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        LOGGER.error(
            "Discord heartbeat failed repo=%s issue=%s agent=%s http_status=%s body=%s",
            repo_name,
            issue_number,
            agent,
            exc.code,
            body,
        )
        return {"sent": False, "http_status": exc.code, "error": body, "agent": agent}
    except URLError as exc:
        LOGGER.error(
            "Discord heartbeat failed repo=%s issue=%s agent=%s error=%s",
            repo_name,
            issue_number,
            agent,
            exc,
        )
        return {"sent": False, "error": str(exc), "agent": agent}


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
    event_label = (payload.get("label") or {}).get("name", "")

    return {
        "delivery_id": delivery_id,
        "event_type": event_type,
        "action": payload.get("action", ""),
        "repository_full_name": repository.get("full_name", ""),
        "issue_number": issue.get("number"),
        "issue_title": issue.get("title", ""),
        "issue_url": issue.get("html_url", ""),
        "issue_body": issue.get("body", ""),
        "issue_state": issue.get("state", ""),
        "labels": labels,
        "event_label": event_label,
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
        if issue_state != "open" or action not in SUPPORTED_ISSUE_ACTIONS:
            return False
        if action == "labeled":
            event_label = (normalized_event.get("event_label") or "").strip().lower()
            return event_label in {DISPATCH_READY_LABEL, STATUS_DONE_LABEL}
        return True

    if event_type == "issue_comment":
        if action not in SUPPORTED_COMMENT_ACTIONS:
            return False
        body = (normalized_event.get("comment_body") or "").strip()
        lowered = body.lower()
        return (
            body.startswith("/retry")
            or body.startswith("/status")
            or body.startswith("/hold")
            or "status: done" in lowered
            or "status: blocked" in lowered
            or "status: failed" in lowered
            or "status:done" in lowered
            or "status:blocked" in lowered
            or "status:failed" in lowered
        )

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
