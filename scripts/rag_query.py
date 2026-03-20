#!/usr/bin/env python3
from __future__ import annotations

import json

from rag_common import DEFAULT_TOP_K, cfg_from_args, common_parser, query_records


def main() -> int:
    parser = common_parser("Query Mac Mini LanceDB RAG")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=DEFAULT_TOP_K)
    args = parser.parse_args()

    cfg = cfg_from_args(args)
    results = query_records(args.query, cfg, args.limit)
    print(json.dumps({"ok": True, "action": "query", "query": args.query, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
