"""Utility to maintain the aether session registry used by the relay ingress."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the aether session registry entry.")
    parser.add_argument("label", help="Session label to register (e.g. aether-ops-inbox)")
    parser.add_argument("session_id", help="Session ID that corresponds to the label")
    parser.add_argument(
        "--registry",
        default="~/.openclaw/workspace/aether_session_registry.json",
        help="Path to the registry file",
    )
    args = parser.parse_args()

    registry_path = Path(args.registry).expanduser()
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(registry_path.read_text())
    except Exception:
        data = {}

    entry = {
        "sessionId": args.session_id,
        "updatedAt": int(registry_path.stat().st_mtime) if registry_path.exists() else int(time.time()),
    }
    data[args.label] = entry
    registry_path.write_text(json.dumps(data, indent=2))
    print(f"Wrote {args.label} -> {args.session_id} into {registry_path}")


if __name__ == "__main__":
    main()
