#!/usr/bin/env python3
from __future__ import annotations

import json

from rag_common import cfg_from_args, common_parser, table_stats


def main() -> int:
    parser = common_parser("Inspect Mac Mini LanceDB RAG stats")
    args = parser.parse_args()
    cfg = cfg_from_args(args)
    print(json.dumps({"ok": True, "action": "stats", **table_stats(cfg)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
