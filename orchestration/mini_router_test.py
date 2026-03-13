from orchestration.router import Router


event = {
    "delivery_id": "mini-delivery-test-2",
    "event_type": "issues",
    "action": "labeled",
    "repository_full_name": "renshangh/real-estate-assistant",
    "issue_number": 157,
    "issue_title": "#154 Working Item: Initialize SQLite database from api/schema.sql",
    "issue_body": "Initialize the local SQLite operational database from api/schema.sql.",
    "issue_state": "open",
    "labels": ["agent:ember", "dispatch:ready"],
    "comment_body": "",
    "sender_login": "renshangh",
    "html_url": "https://github.com/renshangh/real-estate-assistant/issues/157",
    "received_at": "2026-03-13T19:00:00Z",
}

router = Router(ledger_path="orchestration/mini_test_run_ledger.sqlite")
result = router.handle_event(event)
print(result["status"])
print(result["agent"])
print(result["runner_result"]["result_status"])
print(result["runner_result"]["summary"][:400])
print(result["runner_result"]["raw_output_path"])
